import os
import math
import RNS
import RNS.vendor.umsgpack as mp

def simulate(link_speed=9600, audio_slot_ms=70, codec_rate=1200, method="msgpack"):
    # Simulated on-air link speed
    LINK_SPEED = link_speed

    # Packing method, can be "msgpack" or "protobuf"
    PACKING_METHOD = method

    # The target audio slot time
    TARGET_MS = audio_slot_ms

    # Packets needed per second for half-duplex audio
    PACKETS_PER_SECOND = 1000/TARGET_MS

    # Effective audio encoder bitrate
    CODEC_RATE = codec_rate

    # Maximum number of supported audio modes
    MAX_ENUM = 127

    # Per-packet overhead on a established link is 19
    # bytes, 3 for header and context, 16 for link ID
    RNS_OVERHEAD = 19

    # Physical-layer overhead. For RNode, this is 1
    # byte per RNS packet.
    PHY_OVERHEAD = 1

    # Total transport overhead
    TRANSPORT_OVERHEAD = PHY_OVERHEAD+RNS_OVERHEAD

    # Calculate parameters
    AUDIO_LEN = int(math.ceil(CODEC_RATE/(1000/TARGET_MS)/8))
    PER_BYTE_LATENCY_MS = 1000/(LINK_SPEED/8)

    # Pack the message with msgpack to get real-
    # world packed message size

    if PACKING_METHOD == "msgpack":
        # Calculate msgpack overhead
        PL_LEN = len(mp.packb([MAX_ENUM, os.urandom(AUDIO_LEN)]))
        PACKING_OVERHEAD = PL_LEN-AUDIO_LEN
    elif PACKING_METHOD == "protobuf":
        # For protobuf, assume the 8 bytes of stated overhead
        PACKING_OVERHEAD = 8
        PL_LEN = AUDIO_LEN+PACKING_OVERHEAD
    else:
        print("Unsupported packing method")
        exit(1)

    # Calculate required encrypted token blocks
    BLOCKSIZE = 16
    REQUIRED_BLOCKS = math.ceil((PL_LEN+1)/BLOCKSIZE)
    ENCRYPTED_PAYLOAD_LEN = REQUIRED_BLOCKS*BLOCKSIZE
    BLOCK_HEADROOM = (REQUIRED_BLOCKS*BLOCKSIZE) - PL_LEN - 1

    # The complete on-air packet length
    PACKET_LEN     = PHY_OVERHEAD+RNS_OVERHEAD+ENCRYPTED_PAYLOAD_LEN
    PACKET_LATENCY = round(PACKET_LEN*PER_BYTE_LATENCY_MS, 1)

    # TODO: This should include any additional
    # airtime consumption such as preamble and TX-tail.
    PACKET_AIRTIME = PACKET_LEN*PER_BYTE_LATENCY_MS
    AIRTIME_PCT = (PACKET_AIRTIME/TARGET_MS) * 100

    # Maximum amount of concurrent full-duplex
    # calls that can coexist on the same channel
    CONCURRENT_CALLS = math.floor(100/AIRTIME_PCT)

    # Calculate latencies
    TRANSPORT_LATENCY  = round((PHY_OVERHEAD+RNS_OVERHEAD)*PER_BYTE_LATENCY_MS, 1)

    PAYLOAD_LATENCY    = round(ENCRYPTED_PAYLOAD_LEN*PER_BYTE_LATENCY_MS, 1)
    RAW_DATA_LATENCY   = round(AUDIO_LEN*PER_BYTE_LATENCY_MS, 1)
    PACKING_LATENCY    = round(PACKING_OVERHEAD*PER_BYTE_LATENCY_MS, 1)
    
    DATA_LATENCY       = round(ENCRYPTED_PAYLOAD_LEN*PER_BYTE_LATENCY_MS, 1)
    ENCRYPTION_LATENCY = round((ENCRYPTED_PAYLOAD_LEN-PL_LEN)*PER_BYTE_LATENCY_MS, 1)
    if ENCRYPTED_PAYLOAD_LEN-PL_LEN == 1:
        E_OPT_STR = "(optimal)"
    else:
        E_OPT_STR = "(sub-optimal)"

    TOTAL_LATENCY      = round(TARGET_MS+PACKET_LATENCY, 1)

    print( "\n===== Simulation Parameters ===\n")
    print(f"  Packing method       : {method}")
    print(f"  Sampling delay       : {TARGET_MS}ms")
    print(f"  Codec bitrate        : {CODEC_RATE} bps")
    print(f"  Audio data           : {AUDIO_LEN} bytes")
    print(f"  Packing overhead     : {PACKING_OVERHEAD} bytes")
    print(f"  Payload length       : {PL_LEN} bytes")
    print(f"  AES blocks needed    : {REQUIRED_BLOCKS}")
    print(f"  Encrypted payload    : {ENCRYPTED_PAYLOAD_LEN} bytes")
    print(f"  Transport overhead   : {TRANSPORT_OVERHEAD} bytes ({RNS_OVERHEAD} from RNS, {PHY_OVERHEAD} from PHY)")
    print(f"  On-air length        : {PACKET_LEN} bytes")
    print(f"  Packet airtime       : {round(PACKET_AIRTIME,2)}ms")

    print( "\n===== Results for "+RNS.prettyspeed(LINK_SPEED)+" Link Speed ===\n")
    print(f"  Final latency        : {TOTAL_LATENCY}ms")
    print(f"    Recording latency  : contributes {TARGET_MS}ms")
    print(f"    Packet transport   : contributes {PACKET_LATENCY}ms")
    print(f"      Payload          : contributes {PAYLOAD_LATENCY}ms")
    print(f"        Audio data     : contributes {RAW_DATA_LATENCY}ms")
    print(f"        Packing format : contributes {PACKING_LATENCY}ms")
    print(f"        Encryption     : contributes {ENCRYPTION_LATENCY}ms {E_OPT_STR}")
    print(f"      RNS+PHY overhead : contributes {TRANSPORT_LATENCY}ms")
    print(f"")
    print(f"  Half-duplex airtime  : {round(AIRTIME_PCT, 2)}% of link capacity")
    print(f"    Concurrent calls   : {int(CONCURRENT_CALLS)}\n")
    print(f"  Full-duplex airtime  : {round(AIRTIME_PCT*2, 2)}% of link capacity")
    print(f"    Concurrent calls   : {int(CONCURRENT_CALLS/2)}")

    if BLOCK_HEADROOM != 0:
        print("")
        print(f"  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"  Unaligned AES block! Each packet could fit")
        print(f"  {BLOCK_HEADROOM} bytes of additional audio data")
        print(f"  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

print(  "\n= With mspack =================")
simulate(method="msgpack")

#print("\n\n= With protobuf ===============")
#simulate(method="protobuf")
