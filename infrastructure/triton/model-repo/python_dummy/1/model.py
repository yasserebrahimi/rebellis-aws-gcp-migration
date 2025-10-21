import numpy as np
import triton_python_backend_utils as pb_utils

class TritonPythonModel:
    def initialize(self, args): pass
    def execute(self, requests):
        responses = []
        for req in requests:
            in_tensor = pb_utils.get_input_tensor_by_name(req, "INPUT0").as_numpy().astype(np.float32)
            out_tensor = pb_utils.Tensor("OUTPUT0", in_tensor * 2.0)
            responses.append(pb_utils.InferenceResponse(output_tensors=[out_tensor]))
        return responses
    def finalize(self): pass
