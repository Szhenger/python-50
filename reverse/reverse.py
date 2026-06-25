import sys
import struct
from dataclasses import dataclass

# Fixed-size WAV Header structure (44 bytes total)
# Equivalent to C/C++ packed struct
WAVHEADER_FORMAT = '<4sI4s4sIHHIIHH4sI'

@dataclass
class WAVHEADER:
    chunkId: bytes          # 4 bytes (e.g., "RIFF")
    chunkSize: int          # 4 bytes (unsigned int)
    format: bytes           # 4 bytes (e.g., "WAVE")
    subchunk1Id: bytes      # 4 bytes (e.g., "fmt ")
    subchunk1Size: int      # 4 bytes (unsigned int)
    audioFormat: int        # 2 bytes (unsigned short)
    numChannels: int        # 2 bytes (unsigned short)
    sampleRate: int         # 4 bytes (unsigned int)
    byteRate: int           # 4 bytes (unsigned int)
    blockAlign: int         # 2 bytes (unsigned short)
    bitsPerSample: int      # 2 bytes (unsigned short)
    subchunk2Id: bytes      # 4 bytes (e.g., "data")
    subchunk2Size: int      # 4 bytes (unsigned int)

def check_format(header: WAVHEADER) -> bool:
    """Returns True when the header's format field is b'WAVE'."""
    return header.format == b'WAVE'

def get_block_size(header: WAVHEADER) -> int:
    """Returns the size in bytes of one audio block (one sample across all channels)."""
    return (header.numChannels * header.bitsPerSample) // 8

def main() -> int:
    # Ensure proper usage
    if len(sys.argv) != 3:
        print("Usage: python reverse.py input.wav output.wav", file=sys.stderr)
        return 1

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    header_size = struct.calcsize(WAVHEADER_FORMAT)

    # Open input file in binary read mode
    try:
        with open(input_path, "rb") as infile:
            header_data = infile.read(header_size)
            if len(header_data) < header_size:
                print("Error: Could not read WAV header.", file=sys.stderr)
                return 1

            # Unpack binary data into WAVHEADER dataclass
            unpacked = struct.unpack(WAVHEADER_FORMAT, header_data)
            header = WAVHEADER(*unpacked)

            # Validate WAV format
            if not check_format(header):
                print("Error: Input is not a WAV file.", file=sys.stderr)
                return 1

            # Calculate block size and blocks count
            block_size = get_block_size(header)
            
            infile.seek(0, 2)
            file_size = infile.tell()
            audio_size = file_size - header_size
            num_blocks = audio_size // block_size

            # Open output file in binary write mode
            with open(output_path, "wb") as outfile:
                # Write identical header to output
                outfile.write(header_data)

                # Read and write blocks in reverse order
                for i in range(num_blocks):
                    offset = header_size + (num_blocks - (i + 1)) * block_size
                    infile.seek(offset)
                    block_buffer = infile.read(block_size)
                    outfile.write(block_buffer)
                    
    except IOError:
        print("Error: Cannot open file.", file=sys.stderr)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
