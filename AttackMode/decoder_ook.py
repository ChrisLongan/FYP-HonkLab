#!/usr/bin/env python3
"""
Simplified OOK Decoder - Direct Binary Signal Following
Directly converts binary signal to bit stream: 1.0 = '1', 0.0 = '0'
Wide rectangles = multiple consecutive bits
"""

import struct
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple, List
from dataclasses import dataclass
import argparse
import os
from datetime import datetime


@dataclass
class OokPulse:
    """Represents a single OOK pulse with timing and frequency information"""
    hi_nanoseconds: int
    low_nanoseconds: int
    frequency_offset_hz: int = 0


@dataclass
class OokBurst:
    """Represents a burst of OOK pulses"""
    position_nanoseconds: int = 0
    pulses: List[OokPulse] = None
    
    def __post_init__(self):
        if self.pulses is None:
            self.pulses = []
    
    def add_pulse(self, hi_ns: int, low_ns: int, freq_offset_hz: int = 0) -> bool:
        """Add a pulse to the burst"""
        self.pulses.append(OokPulse(hi_ns, low_ns, freq_offset_hz))
        return True
    
    def pulse_count(self) -> int:
        """Get number of pulses in burst"""
        return len(self.pulses)


class SimplifiedOokConverter:
    """Simplified converter that directly follows the binary signal"""
    
    def __init__(self, sample_rate: float = 2e6, debug: bool = False):
        self.sample_rate = sample_rate
        self.debug = debug
    
    def load_iq_file(self, filename: str, dtype=np.complex64) -> Optional[np.ndarray]:
        """Load IQ samples from file"""
        try:
            iq_data = np.fromfile(filename, dtype=dtype)
            print(f"[INFO] Loaded {len(iq_data)} samples from {filename}")
            return iq_data
        except Exception as e:
            print(f"[ERROR] Failed to load file: {e}")
            return None
    
    def extract_bits_direct(self, iq_samples: np.ndarray) -> str:
        """
        Directly extract bits from IQ signal by following the binary pattern.
        Improved version with better sampling and threshold handling.
        """
        print("[INFO] Direct bit extraction from binary signal...")
        
        # Convert to envelope
        envelope = np.abs(iq_samples)
        
        # Slightly more aggressive smoothing to clean up transitions
        window_size = max(int(self.sample_rate * 3e-6), 5)  # 3µs window, minimum 5 samples
        if window_size > 1:
            envelope = np.convolve(envelope, np.ones(window_size)/window_size, mode='same')
        
        # Calculate threshold - use a more conservative approach
        threshold = self._calculate_adaptive_threshold(envelope)
        
        # Create binary signal
        binary_signal = envelope > threshold
        
        # Additional cleaning: remove very short pulses/gaps
        from scipy.ndimage import binary_opening, binary_closing
        
        # Fill small gaps (closing operation)
        binary_signal = binary_closing(binary_signal, iterations=3)
        # Remove small noise pulses (opening operation)  
        binary_signal = binary_opening(binary_signal, iterations=2)
        
        print(f"[INFO] Using threshold: {threshold:.6f}")
        
        # Find the base bit period
        bit_period_samples = self._estimate_bit_period(binary_signal)
        bit_period_ns = int(bit_period_samples * 1e9 / self.sample_rate)
        
        print(f"[INFO] Estimated base bit period: {bit_period_samples} samples ({bit_period_ns//1000}µs)")
        
        # Use a more robust sampling strategy
        # Instead of sampling at regular intervals, follow the actual signal structure
        bits = self._extract_bits_by_runs(binary_signal, bit_period_samples)
        
        bit_string = ''.join(bits)
        print(f"[INFO] Extracted {len(bits)} bits: {bit_string}")
        
        if self.debug:
            self._plot_direct_analysis(envelope, binary_signal, threshold, bits, bit_period_samples)
        
        return bit_string
    
    def _extract_bits_by_runs(self, binary_signal: np.ndarray, bit_period_samples: int) -> List[str]:
        """
        Extract bits by analyzing runs of consecutive 1s and 0s.
        This is more accurate than fixed-interval sampling.
        """
        print("[INFO] Extracting bits by analyzing runs...")
        
        # Find runs of consecutive values
        changes = np.diff(np.concatenate(([0], binary_signal, [0])))
        run_starts = np.where(changes == 1)[0]
        run_ends = np.where(changes == -1)[0]
        
        if len(run_starts) == 0 or len(run_ends) == 0:
            print("[WARN] No clear runs found, falling back to regular sampling")
            return self._extract_bits_regular_sampling(binary_signal, bit_period_samples)
        
        bits = []
        
        # Process each run
        for i in range(max(len(run_starts), len(run_ends))):
            # Handle high runs (1s)
            if i < len(run_starts) and i < len(run_ends):
                high_start = run_starts[i]
                high_end = run_ends[i]
                high_length = high_end - high_start
                
                # Convert run length to number of bits
                num_ones = max(1, round(high_length / bit_period_samples))
                bits.extend(['1'] * num_ones)
                
                if self.debug:
                    print(f"[DEBUG] High run: {high_length} samples ({high_length * 1000 // bit_period_samples / 10:.1f} bit periods) -> {num_ones} ones")
            
            # Handle low runs (0s) - gap between this run end and next run start
            if i < len(run_ends) and (i + 1) < len(run_starts):
                low_start = run_ends[i]
                low_end = run_starts[i + 1]
                low_length = low_end - low_start
                
                # Only add 0s if the gap is significant
                if low_length >= bit_period_samples * 0.5:  # At least half a bit period
                    num_zeros = max(1, round(low_length / bit_period_samples))
                    bits.extend(['0'] * num_zeros)
                    
                    if self.debug:
                        print(f"[DEBUG] Low run: {low_length} samples ({low_length * 1000 // bit_period_samples / 10:.1f} bit periods) -> {num_zeros} zeros")
            
            # Handle the final gap after the last high run
            elif i == len(run_starts) - 1 and i < len(run_ends):
                remaining_samples = len(binary_signal) - run_ends[i]
                if remaining_samples >= bit_period_samples * 0.5:
                    num_zeros = max(1, round(remaining_samples / bit_period_samples))
                    bits.extend(['0'] * num_zeros)
                    
                    if self.debug:
                        print(f"[DEBUG] Final low run: {remaining_samples} samples -> {num_zeros} zeros")
        
        return bits
    
    def _extract_bits_regular_sampling(self, binary_signal: np.ndarray, bit_period_samples: int) -> List[str]:
        """
        Fallback method: regular interval sampling with larger windows for stability
        """
        print("[INFO] Using regular sampling fallback...")
        
        total_samples = len(binary_signal)
        estimated_total_bits = total_samples // bit_period_samples
        
        bits = []
        
        # Use larger sampling windows to avoid transition regions
        sample_window_size = bit_period_samples // 3  # Use 1/3 of bit period as window
        
        for bit_idx in range(estimated_total_bits):
            # Sample from the center of each bit period
            center_position = int((bit_idx + 0.5) * bit_period_samples)
            
            # Define sampling window around center
            window_start = max(0, center_position - sample_window_size // 2)
            window_end = min(len(binary_signal), center_position + sample_window_size // 2)
            
            if window_end > window_start:
                # Take majority vote in this window
                window_samples = binary_signal[window_start:window_end]
                avg_value = np.mean(window_samples)
                
                # Use a more decisive threshold (0.7 instead of 0.5)
                bit_value = '1' if avg_value > 0.7 else '0'
                bits.append(bit_value)
                
                if self.debug:
                    print(f"[DEBUG] Bit {bit_idx}: center at {center_position}, window [{window_start}:{window_end}], avg = {avg_value:.3f} -> {bit_value}")
            
        return bits
    
    def _estimate_bit_period(self, binary_signal: np.ndarray) -> int:
        """Estimate the basic bit period from the binary signal using a more robust method"""
        # Find transitions
        transitions = np.diff(binary_signal.astype(int))
        transition_indices = np.where(transitions != 0)[0]
        
        if len(transition_indices) < 4:
            # Fallback: divide signal into reasonable number of bits
            return len(binary_signal) // 128  # Try smaller bit periods
        
        # Calculate all interval lengths between transitions
        intervals = np.diff(transition_indices)
        
        if len(intervals) == 0:
            return len(binary_signal) // 128
        
        print(f"[DEBUG] Found {len(intervals)} intervals, range: {min(intervals)}-{max(intervals)} samples")
        
        # Filter out very short noise intervals (less than 50 samples at 2MHz = 25µs)
        min_reasonable_interval = max(50, len(binary_signal) // 2000)
        valid_intervals = intervals[intervals >= min_reasonable_interval]
        
        if len(valid_intervals) == 0:
            print("[DEBUG] No valid intervals found, using all intervals")
            valid_intervals = intervals
        
        print(f"[DEBUG] Valid intervals: {sorted(valid_intervals)[:10]}...")  # Show first 10
        
        # Use the shortest valid interval as it's likely the base bit period
        # But also check if it's reasonable
        shortest_interval = min(valid_intervals)
        
        # The base bit period should give us a reasonable total bit count
        total_samples = len(binary_signal)
        estimated_bits = total_samples / shortest_interval
        
        print(f"[DEBUG] Shortest interval: {shortest_interval} samples, would give {estimated_bits:.1f} bits")
        
        # If the shortest interval gives too many bits, try some multiples
        if estimated_bits > 1000:  # Too many bits
            # Try 2x, 3x, 4x the shortest interval
            for multiplier in [2, 3, 4, 5]:
                candidate = shortest_interval * multiplier
                candidate_bits = total_samples / candidate
                print(f"[DEBUG] Trying {multiplier}x: {candidate} samples = {candidate_bits:.1f} bits")
                if 50 <= candidate_bits <= 800:  # Reasonable range
                    return int(candidate)
        
        # If shortest is reasonable, use it
        if 50 <= estimated_bits <= 800:
            return int(shortest_interval)
        
        # Final fallback: use a fraction of the signal length
        fallback_period = len(binary_signal) // 200  # Assume ~200 bits
        print(f"[DEBUG] Using fallback period: {fallback_period} samples")
        return max(fallback_period, 100)  # At least 100 samples (50µs at 2MHz)
    
    def _calculate_adaptive_threshold(self, envelope: np.ndarray) -> float:
        """Calculate adaptive threshold using a more robust method"""
        
        # Remove extreme outliers first
        p1, p99 = np.percentile(envelope, [1, 99])
        cleaned_envelope = envelope[(envelope >= p1) & (envelope <= p99)]
        
        # Use histogram-based approach for better threshold selection
        hist, bin_edges = np.histogram(cleaned_envelope, bins=100)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # Find the valley between noise floor and signal peaks
        # Look for minimum in the middle region of the histogram
        start_idx = len(hist) // 4  # Skip the first 25%
        end_idx = 3 * len(hist) // 4  # Stop at 75%
        
        if start_idx < end_idx:
            middle_section = hist[start_idx:end_idx]
            valley_idx = start_idx + np.argmin(middle_section)
            threshold = bin_centers[valley_idx]
        else:
            # Fallback to percentile method
            threshold = np.percentile(cleaned_envelope, 60)  # 60th percentile
        
        # Ensure threshold is reasonable
        min_thresh = np.percentile(envelope, 40)
        max_thresh = np.percentile(envelope, 80)
        threshold = np.clip(threshold, min_thresh, max_thresh)
        
        return threshold
    
    def _plot_direct_analysis(self, envelope: np.ndarray, binary_signal: np.ndarray, 
                             threshold: float, bits: List[str], bit_period_samples: int):
        """Plot the direct analysis for debugging"""
        fig, axes = plt.subplots(4, 1, figsize=(15, 12))
        
        time_axis = np.arange(len(envelope)) / self.sample_rate
        
        # Plot 1: Original envelope and threshold
        axes[0].plot(time_axis, envelope, 'b-', alpha=0.7, label='Envelope')
        axes[0].axhline(y=threshold, color='r', linestyle='--', label=f'Threshold ({threshold:.3f})')
        axes[0].set_title('Signal Envelope and Threshold')
        axes[0].set_ylabel('Amplitude')
        axes[0].legend()
        axes[0].grid(True)
        
        # Plot 2: Binary signal with bit sampling points
        axes[1].plot(time_axis, binary_signal.astype(int), 'g-', linewidth=2, label='Binary Signal')
        
        # Add vertical lines showing where we sample each bit
        for bit_idx in range(len(bits)):
            sample_position = int((bit_idx + 0.5) * bit_period_samples)
            if sample_position < len(time_axis):
                sample_time = time_axis[sample_position]
                axes[1].axvline(x=sample_time, color='red', linestyle=':', alpha=0.7)
        
        axes[1].set_title('Binary Signal with Bit Sampling Points')
        axes[1].set_ylabel('Binary Level')
        axes[1].legend()
        axes[1].grid(True)
        
        # Plot 3: Extracted bits
        bit_indices = range(len(bits))
        bit_values = [1 if b == '1' else 0 for b in bits]
        
        axes[2].stem(bit_indices, bit_values, basefmt=' ')
        axes[2].set_title(f'Extracted {len(bits)} Bits')
        axes[2].set_ylabel('Bit Value')
        axes[2].set_xlabel('Bit Index')
        axes[2].set_ylim(-0.5, 1.5)
        axes[2].grid(True)
        
        # Plot 4: Bit pattern analysis
        # Show the bit string in groups for easier reading
        axes[3].text(0.02, 0.8, f"Extracted Pattern:", transform=axes[3].transAxes, fontsize=12, fontweight='bold')
        
        # Display bits in groups of 8
        bit_string = ''.join(bits)
        lines = []
        for i in range(0, len(bit_string), 32):  # 32 bits per line for readability
            line = bit_string[i:i+32]
            # Add spaces every 8 bits
            spaced_line = ' '.join([line[j:j+8] for j in range(0, len(line), 8)])
            lines.append(f"Bits {i:3d}-{min(i+31, len(bit_string)-1):3d}: {spaced_line}")
        
        for idx, line in enumerate(lines):
            axes[3].text(0.02, 0.6 - idx*0.15, line, transform=axes[3].transAxes, 
                        fontsize=10, fontfamily='monospace')
        
        axes[3].set_xlim(0, 1)
        axes[3].set_ylim(0, 1)
        axes[3].set_title('Bit Pattern Analysis')
        axes[3].axis('off')
        
        plt.tight_layout()
        plt.show()
    
    def signal_to_ook_burst(self, iq_samples: np.ndarray) -> Optional[OokBurst]:
        """Convert IQ signal to OOK burst (compatibility wrapper)"""
        bit_string = self.extract_bits_direct(iq_samples)
        
        if not bit_string:
            return None
        
        # Create a dummy burst for compatibility with existing decoder interface
        burst = OokBurst(position_nanoseconds=int(datetime.now().timestamp() * 1e9))
        
        # Convert each bit to a "pulse" for compatibility
        bit_duration_ns = 1000000  # 1ms default
        
        for bit in bit_string:
            if bit == '1':
                hi_ns = int(bit_duration_ns * 0.8)
                low_ns = int(bit_duration_ns * 0.2)
            else:
                hi_ns = int(bit_duration_ns * 0.2)
                low_ns = int(bit_duration_ns * 0.8)
            
            burst.add_pulse(hi_ns, low_ns, 0)
        
        return burst


class SimplifiedOokDecoder:
    """Simplified OOK decoder that works directly with bit strings"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def decode_direct_bits(self, bit_string: str) -> Tuple[str, int]:
        """Decode a bit string directly"""
        return bit_string, len(bit_string)
    
    def analyze_bit_string(self, bit_string: str) -> dict:
        """Analyze bit string and return statistics"""
        if not bit_string:
            return {}
        
        ones_count = bit_string.count('1')
        zeros_count = bit_string.count('0')
        
        stats = {
            'total_bits': len(bit_string),
            'ones_count': ones_count,
            'zeros_count': zeros_count,
            'ones_percentage': (ones_count / len(bit_string)) * 100,
            'zeros_percentage': (zeros_count / len(bit_string)) * 100,
            'pattern_start': bit_string[:16] + '...' if len(bit_string) > 16 else bit_string,
            'pattern_end': '...' + bit_string[-16:] if len(bit_string) > 16 else bit_string
        }
        
        # Look for common patterns
        patterns = []
        if '1010' in bit_string:
            patterns.append("Alternating pattern (1010)")
        if bit_string.startswith('1111') or bit_string.startswith('0000'):
            patterns.append("Preamble detected")
        if '11111111' in bit_string:
            patterns.append("Long high sequence")
        if '00000000' in bit_string:
            patterns.append("Long low sequence")
        
        stats['detected_patterns'] = patterns
        
        return stats


class SimplifiedOokProcessor:
    """Main processor class for simplified OOK decoding"""
    
    def __init__(self, sample_rate: float = 2e6, verbose: bool = False, debug: bool = False):
        self.converter = SimplifiedOokConverter(sample_rate, debug)
        self.decoder = SimplifiedOokDecoder(verbose)
        self.verbose = verbose
    
    def process_file(self, filename: str, output_file: str = "decoded.txt") -> bool:
        """Process an IQ file and extract decoded bits"""
        print(f"[INFO] Processing file: {filename}")
        print(f"[INFO] Using simplified direct bit extraction")
        
        # Load signal
        iq_samples = self.converter.load_iq_file(filename)
        if iq_samples is None:
            return False
        
        # Extract bits directly
        bit_string = self.converter.extract_bits_direct(iq_samples)
        
        if not bit_string:
            print("[ERROR] Failed to extract bits from signal")
            return False
        
        # Decode (in this simplified case, just return the bit string)
        decoded_bits, bit_count = self.decoder.decode_direct_bits(bit_string)
        
        # Analyze
        stats = self.decoder.analyze_bit_string(decoded_bits)
        
        if self.verbose:
            print(f"\n[ANALYSIS] Bit String Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        
        print(f"\n[SUCCESS] Extracted {bit_count} bits: {decoded_bits}")
        
        # Save results
        try:
            with open(output_file, 'w') as f:
                f.write(f"# Simplified OOK Decoder Results\n")
                f.write(f"# Decoded on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Source file: {filename}\n")
                f.write(f"# Method: Direct Binary Signal Following\n")
                f.write(f"# Total bits: {bit_count}\n")
                f.write(f"# Ones: {stats.get('ones_count', 0)} ({stats.get('ones_percentage', 0):.1f}%)\n")
                f.write(f"# Zeros: {stats.get('zeros_count', 0)} ({stats.get('zeros_percentage', 0):.1f}%)\n")
                
                if stats.get('detected_patterns'):
                    f.write(f"# Detected patterns: {', '.join(stats['detected_patterns'])}\n")
                
                f.write(f"#\n")
                f.write(f"# Raw binary data:\n")
                f.write(decoded_bits)
                f.write('\n')
                
                # Add formatted output
                f.write(f"\n# Formatted binary (8-bit groups):\n")
                for i in range(0, len(decoded_bits), 8):
                    group = decoded_bits[i:i+8]
                    f.write(f"# {i//8:03d}: {group}\n")
                
                # Add hex if multiple of 8 bits
                if len(decoded_bits) % 8 == 0:
                    f.write(f"\n# Hexadecimal representation:\n")
                    hex_values = []
                    for i in range(0, len(decoded_bits), 8):
                        byte = decoded_bits[i:i+8]
                        hex_val = hex(int(byte, 2))[2:].upper().zfill(2)
                        hex_values.append(hex_val)
                    f.write(f"# {' '.join(hex_values)}\n")
            
            print(f"[INFO] Results saved to {output_file}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to save results: {e}")
            return False


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='Simplified OOK Signal Decoder - Direct Binary Following')
    parser.add_argument('input_file', nargs='?', help='Input IQ file')
    parser.add_argument('-o', '--output', default='decoded.txt', help='Output file')
    parser.add_argument('-s', '--sample-rate', type=float, default=2e6, help='Sample rate in Hz')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug plots')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive or args.input_file is None:
        print("=" * 60)
        print("    Simplified OOK Signal Decoder")
        print("    Direct Binary Signal Following")
        print("=" * 60)
        
        while True:
            input_file = input("\nEnter IQ file path: ").strip().strip('"')
            if not input_file:
                print("Please enter a file path.")
                continue
            if not os.path.exists(input_file):
                print(f"File '{input_file}' not found.")
                continue
            break
        
        output_file = input("\nOutput file [decoded.txt]: ").strip()
        if not output_file:
            output_file = "decoded.txt"
        
        sample_rate_input = input("\nSample rate [2000000]: ").strip()
        if sample_rate_input:
            try:
                sample_rate = float(sample_rate_input)
            except ValueError:
                sample_rate = 2e6
        else:
            sample_rate = 2e6
        
        verbose = input("\nVerbose output? (y/n) [n]: ").strip().lower() == 'y'
        debug = input("Debug plots? (y/n) [n]: ").strip().lower() == 'y'
        
    else:
        input_file = args.input_file
        output_file = args.output
        sample_rate = args.sample_rate
        verbose = args.verbose
        debug = args.debug
    
    # Process the file
    processor = SimplifiedOokProcessor(sample_rate, verbose, debug)
    success = processor.process_file(input_file, output_file)
    
    if success:
        print(f"\n{'='*60}")
        print(f"[SUCCESS] Processing completed successfully!")
        print(f"[INFO] Decoded bits saved to: {output_file}")
        print(f"[INFO] Method: Direct Binary Signal Following")
        print(f"[INFO] Ready for CC1101 replay attack!")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print(f"[FAILED] Processing failed!")
        print(f"[INFO] Enable debug mode (-d) to analyze the signal")
        print(f"{'='*60}")
    
    if args.interactive or args.input_file is None:
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
