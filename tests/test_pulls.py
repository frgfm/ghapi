import pytest

from ghapi.pulls import PullRequest, parse_diff_body, parse_file_diff
from ghapi.repos import Repository


@pytest.mark.parametrize(
    "file_diff, expected_parsing",
    [
        # https://github.com/frgfm/torch-cam/pull/115
        [
            'a/dummy_lib/core.py b/dummy_lib/core.py\nindex e52afda..cced706 100644\n--- a/dummy_lib/core.py\n+++ b/dummy_lib/core.py\n@@ -1,12 +1,12 @@\n # Copyright (C) 2022, François-Guillaume Fernandez.\n-\n # This program is licensed under the Apache License 2.0.\n # See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.\n-\n from enum import Enum\n from typing import List\n \n-__all__ = ["greet_contributor", "convert_temperature_sequences", "TemperatureScale"]\n+__all__ = [\n+    "greet_contributor", "convert_temperature_sequences", "TemperatureScale"\n+]\n \n \n class TemperatureScale(Enum):\n@@ -47,9 +47,14 @@ def convert_temperature_sequences(\n     if input_scale == output_scale:\n         return input_temperatures\n \n-    if input_scale == TemperatureScale.FAHRENHEIT and output_scale == TemperatureScale.CELSIUS:\n-        return [(fahrenheit_temp - 32) * 5 / 9 for fahrenheit_temp in input_temperatures]\n-    elif input_scale == TemperatureScale.CELSIUS and output_scale == TemperatureScale.FAHRENHEIT:\n-        return [celsius_temp * 9 / 5 + 32 for celsius_temp in input_temperatures]\n+    if (input_scale == TemperatureScale.FAHRENHEIT\n+            and output_scale == TemperatureScale.CELSIUS):\n+        return [(fahrenheit_temp - 32) * 5 / 9\n+                for fahrenheit_temp in input_temperatures]\n+    elif (input_scale == TemperatureScale.CELSIUS\n+          and output_scale == TemperatureScale.FAHRENHEIT):\n+        return [\n+            celsius_temp * 9 / 5 + 32 for celsius_temp in input_temperatures\n+        ]\n \n     raise NotImplementedError\n'.split(  # noqa: E501
                "\n"
            ),
            [(2, 2, None, None, 6, 6), (5, 5, None, None, 9, 9), (9, 9, 7, 9, 13, 16), (50, 53, 50, 58, 24, 36)],
        ],
    ],
)
def test_parse_file_diff(file_diff, expected_parsing):
    out = parse_file_diff(file_diff)
    assert out == expected_parsing


@pytest.mark.parametrize(
    "diff_body, expected_parsing",
    [
        # https://github.com/frgfm/torch-cam/pull/187
        [
            'diff --git a/tests/test_methods_activation.py b/tests/test_methods_activation.py\nindex df90c23..2a41d08 100644\n--- a/tests/test_methods_activation.py\n+++ b/tests/test_methods_activation.py\n@@ -20,7 +20,7 @@ def _verify_cam(activation_map, output_size):\n     # Simple verifications\n     assert isinstance(activation_map, torch.Tensor)\n     assert activation_map.shape == output_size\n-    assert not torch.any(torch.isnan(activation_map))\n+    assert not torch.isnan(activation_map).any()\n \n \n @pytest.mark.parametrize(\ndiff --git a/tests/test_methods_gradient.py b/tests/test_methods_gradient.py\nindex 5aecad5..6022c1a 100644\n--- a/tests/test_methods_gradient.py\n+++ b/tests/test_methods_gradient.py\n@@ -10,7 +10,7 @@ def _verify_cam(activation_map, output_size):\n     # Simple verifications\n     assert isinstance(activation_map, torch.Tensor)\n     assert activation_map.shape == output_size\n-    assert not torch.any(torch.isnan(activation_map))\n+    assert not torch.isnan(activation_map).any()\n \n \n @pytest.mark.parametrize(\ndiff --git a/torchcam/methods/gradient.py b/torchcam/methods/gradient.py\nindex 610523f..08ae3c8 100644\n--- a/torchcam/methods/gradient.py\n+++ b/torchcam/methods/gradient.py\n@@ -149,7 +149,9 @@ class GradCAMpp(_GradCAM):\n         input_shape: shape of the expected input tensor excluding the batch dimension\n     """\n \n-    def _get_weights(self, class_idx: Union[int, List[int]], scores: Tensor, **kwargs: Any) -> List[Tensor]:\n+    def _get_weights(\n+        self, class_idx: Union[int, List[int]], scores: Tensor, eps: float = 1e-8, **kwargs: Any\n+    ) -> List[Tensor]:\n         """Computes the weight coefficients of the hooked activation maps."""\n \n         # Backpropagate\n@@ -168,7 +170,7 @@ def _get_weights(self, class_idx: Union[int, List[int]], scores: Tensor, **kwarg\n         nan_mask = [g2 > 0 for g2 in grad_2]\n         alpha = grad_2\n         for idx, d, mask in zip(range(len(grad_2)), denom, nan_mask):\n-            alpha[idx][mask].div_(d[mask])\n+            alpha[idx][mask].div_(d[mask] + eps)\n \n         # Apply pixel coefficient in each weight\n         return [a.mul_(torch.relu(grad)).flatten(2).sum(-1) for a, grad in zip(alpha, self.hook_g)]\n@@ -256,7 +258,7 @@ def _store_input(self, module: nn.Module, input: Tensor) -> None:\n             self._input = input[0].data.clone()\n \n     def _get_weights(\n-        self, class_idx: Union[int, List[int]], scores: Optional[Tensor] = None, **kwargs: Any\n+        self, class_idx: Union[int, List[int]], scores: Optional[Tensor] = None, eps: float = 1e-8, **kwargs: Any\n     ) -> List[Tensor]:\n         """Computes the weight coefficients of the hooked activation maps."""\n \n@@ -292,7 +294,7 @@ def _get_weights(\n         # Alpha coefficient for each pixel\n         spatial_dims = self.hook_a[0].ndim - 2\n         alpha = [\n-            g2 / (2 * g2 + (g3 * act).flatten(2).sum(-1)[(...,) + (None,) * spatial_dims])\n+            g2 / (2 * g2 + (g3 * act).flatten(2).sum(-1)[(...,) + (None,) * spatial_dims] + eps)\n             for g2, g3, act in zip(grad_2, grad_3, init_fmap)\n         ]\n \n@@ -336,7 +338,9 @@ class XGradCAM(_GradCAM):\n         input_shape: shape of the expected input tensor excluding the batch dimension\n     """\n \n-    def _get_weights(self, class_idx: Union[int, List[int]], scores: Tensor, **kwargs: Any) -> List[Tensor]:\n+    def _get_weights(\n+        self, class_idx: Union[int, List[int]], scores: Tensor, eps: float = 1e-8, **kwargs: Any\n+    ) -> List[Tensor]:\n         """Computes the weight coefficients of the hooked activation maps."""\n \n         # Backpropagate\n@@ -344,7 +348,10 @@ def _get_weights(self, class_idx: Union[int, List[int]], scores: Tensor, **kwarg\n \n         self.hook_a: List[Tensor]  # type: ignore[assignment]\n         self.hook_g: List[Tensor]  # type: ignore[assignment]\n-        return [(grad * act).flatten(2).sum(-1) / act.flatten(2).sum(-1) for act, grad in zip(self.hook_a, self.hook_g)]\n+        return [\n+            (grad * act).flatten(2).sum(-1) / act.flatten(2).sum(-1).add(eps)\n+            for act, grad in zip(self.hook_a, self.hook_g)\n+        ]\n \n \n class LayerCAM(_GradCAM):\n',  # noqa: E501
            {
                "tests/test_methods_activation.py": 1,
                "tests/test_methods_gradient.py": 1,
                "torchcam/methods/gradient.py": 6,
            },
        ],
        # https://github.com/frgfm/torch-cam/pull/115
        [
            "diff --git a/.flake8 b/.flake8\nindex daef3984..6cd2696b 100644\n--- a/.flake8\n+++ b/.flake8\n@@ -1,4 +1,5 @@\n [flake8]\n max-line-length = 120\n-ignore = F401, E402, E265, F403, W503, W504, F821, W605\n-exclude = .github, .git, venv*, docs, build\n+ignore = E402, E265, F403, W503, W504, E731\n+exclude = .circleci, .git, venv*, docs, build\n+per-file-ignores = **/__init__.py:F401\n",  # noqa: E501
            {".flake8": 1},
        ],
        # https://github.com/frgfm/ci-benchmark/pull/15/files
        [
            'diff --git a/dummy_lib/core.py b/dummy_lib/core.py\nindex e52afda..cced706 100644\n--- a/dummy_lib/core.py\n+++ b/dummy_lib/core.py\n@@ -1,12 +1,12 @@\n # Copyright (C) 2022, François-Guillaume Fernandez.\n-\n # This program is licensed under the Apache License 2.0.\n # See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.\n-\n from enum import Enum\n from typing import List\n \n-__all__ = ["greet_contributor", "convert_temperature_sequences", "TemperatureScale"]\n+__all__ = [\n+    "greet_contributor", "convert_temperature_sequences", "TemperatureScale"\n+]\n \n \n class TemperatureScale(Enum):\n@@ -47,9 +47,14 @@ def convert_temperature_sequences(\n     if input_scale == output_scale:\n         return input_temperatures\n \n-    if input_scale == TemperatureScale.FAHRENHEIT and output_scale == TemperatureScale.CELSIUS:\n-        return [(fahrenheit_temp - 32) * 5 / 9 for fahrenheit_temp in input_temperatures]\n-    elif input_scale == TemperatureScale.CELSIUS and output_scale == TemperatureScale.FAHRENHEIT:\n-        return [celsius_temp * 9 / 5 + 32 for celsius_temp in input_temperatures]\n+    if (input_scale == TemperatureScale.FAHRENHEIT\n+            and output_scale == TemperatureScale.CELSIUS):\n+        return [(fahrenheit_temp - 32) * 5 / 9\n+                for fahrenheit_temp in input_temperatures]\n+    elif (input_scale == TemperatureScale.CELSIUS\n+          and output_scale == TemperatureScale.FAHRENHEIT):\n+        return [\n+            celsius_temp * 9 / 5 + 32 for celsius_temp in input_temperatures\n+        ]\n \n     raise NotImplementedError\ndiff --git a/tests/test_core.py b/tests/test_core.py\nindex 90d3940..cdecb87 100644\n--- a/tests/test_core.py\n+++ b/tests/test_core.py\n@@ -1,6 +1,8 @@\n import pytest\n \n-from dummy_lib.core import TemperatureScale, convert_temperature_sequences, greet_contributor\n+from dummy_lib.core import convert_temperature_sequences\n+from dummy_lib.core import greet_contributor\n+from dummy_lib.core import TemperatureScale\n \n \n @pytest.mark.parametrize(\n@@ -44,10 +46,13 @@ def test_greet_contributor(name, expected_output):\n             [10, -10.0, 0],\n         ],\n         # Error\n-        [[10, -10.0, 0], TemperatureScale.CELSIUS, "kelvin", NotImplementedError, None],\n+        [[10, -10.0, 0], TemperatureScale.CELSIUS, "kelvin",\n+         NotImplementedError, None],\n     ],\n )\n-def test_convert_temperature_sequences(input_temperatures, input_scale, output_scale, error_type, expected_output):\n+def test_convert_temperature_sequences(input_temperatures, input_scale,\n+                                       output_scale, error_type,\n+                                       expected_output):\n     kwargs = {}\n     if input_scale is not None:\n         kwargs["input_scale"] = input_scale\n@@ -55,7 +60,8 @@ def test_convert_temperature_sequences(input_temperatures, input_scale, output_s\n         kwargs["output_scale"] = output_scale\n \n     if error_type is None:\n-        assert convert_temperature_sequences(input_temperatures, **kwargs) == expected_output\n+        assert (convert_temperature_sequences(input_temperatures,\n+                                              **kwargs) == expected_output)\n     else:\n         with pytest.raises(error_type):\n             convert_temperature_sequences(input_temperatures, **kwargs)\n',  # noqa: E501
            {"dummy_lib/core.py": 4, "tests/test_core.py": 4},
        ],
    ],
)
def test_parse_diff_body(diff_body, expected_parsing):
    out = parse_diff_body(diff_body)
    assert len(out) == len(expected_parsing)
    for file, num_sections in expected_parsing.items():
        assert len(out[file]) == num_sections


@pytest.mark.parametrize(
    "owner, repo, pr_num, payload_len, created_at",
    [
        ["frgfm", "torch-cam", 115, 11, "2021-11-14T16:12:44Z"],
        ["frgfm", "torch-cam", 187, 11, "2022-09-18T17:08:50Z"],
    ],
)
def test_pull_request_get_info(owner, repo, pr_num, payload_len, created_at):
    pr = PullRequest(Repository(owner, repo), pr_num)
    out = pr.get_info()
    assert len(out) == payload_len
    assert out["created_at"] == created_at


@pytest.mark.parametrize(
    "owner, repo, pr_num, num_files, num_sections",
    [
        ["frgfm", "torch-cam", 115, 1, 1],
        ["frgfm", "torch-cam", 187, 3, 8],
    ],
)
def test_pull_request_get_diff(owner, repo, pr_num, num_files, num_sections):
    pr = PullRequest(Repository(owner, repo), pr_num)
    out = pr.get_diff()
    assert len(out) == num_files
    assert sum(len(sections) for sections in out.values()) == num_sections
