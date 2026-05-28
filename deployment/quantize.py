"""Quantize VulGCL to int8 for Raspberry Pi deployment."""
import torch
import onnx
import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic, QuantType


def export_to_onnx(model, sample_inputs, output_path):
    torch.onnx.export(
        model, sample_inputs, output_path,
        opset_version=14,
        input_names=["graph", "image", "input_ids", "attention_mask"],
        output_names=["logits"],
        dynamic_axes={"input_ids": {0: "batch"}, "logits": {0: "batch"}},
    )
    print(f"Exported to {output_path}")


def quantize_model(onnx_path, quantized_path):
    quantize_dynamic(
        onnx_path, quantized_path,
        weight_type=QuantType.QInt8,
    )
    print(f"Quantized model saved to {quantized_path}")


def benchmark(quantized_path, sample_inputs, n_runs=100):
    sess = ort.InferenceSession(quantized_path)
    import time
    times = []
    for _ in range(n_runs):
        t0 = time.perf_counter()
        sess.run(None, sample_inputs)
        times.append(time.perf_counter() - t0)
    avg_ms = (sum(times) / len(times)) * 1000
    print(f"Average inference: {avg_ms:.2f} ms over {n_runs} runs")
    return avg_ms


if __name__ == "__main__":
    # Usage:
    # 1. Load trained VulGCL model
    # 2. Export to ONNX
    # 3. Quantize
    # 4. Benchmark (run this script ON the Raspberry Pi)
    print("Run export_to_onnx() then quantize_model() then benchmark() on Pi.")
