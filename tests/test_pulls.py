import pytest

from ghapi_client.pulls import PullRequest, parse_diff_body


@pytest.mark.parametrize(
    "diff_body, expected_parsing",
    [
        # https://github.com/frgfm/torch-cam/pull/187
        [
            'diff --git a/tests/test_methods_activation.py b/tests/test_methods_activation.py\nindex df90c23..2a41d08 100644\n--- a/tests/test_methods_activation.py\n+++ b/tests/test_methods_activation.py\n@@ -20,7 +20,7 @@ def _verify_cam(activation_map, output_size):\n     # Simple verifications\n     assert isinstance(activation_map, torch.Tensor)\n     assert activation_map.shape == output_size\n-    assert not torch.any(torch.isnan(activation_map))\n+    assert not torch.isnan(activation_map).any()\n \n \n @pytest.mark.parametrize(\ndiff --git a/tests/test_methods_gradient.py b/tests/test_methods_gradient.py\nindex 5aecad5..6022c1a 100644\n--- a/tests/test_methods_gradient.py\n+++ b/tests/test_methods_gradient.py\n@@ -10,7 +10,7 @@ def _verify_cam(activation_map, output_size):\n     # Simple verifications\n     assert isinstance(activation_map, torch.Tensor)\n     assert activation_map.shape == output_size\n-    assert not torch.any(torch.isnan(activation_map))\n+    assert not torch.isnan(activation_map).any()\n \n \n @pytest.mark.parametrize(\ndiff --git a/torchcam/methods/gradient.py b/torchcam/methods/gradient.py\nindex 610523f..08ae3c8 100644\n--- a/torchcam/methods/gradient.py\n+++ b/torchcam/methods/gradient.py\n@@ -149,7 +149,9 @@ class GradCAMpp(_GradCAM):\n         input_shape: shape of the expected input tensor excluding the batch dimension\n     """\n \n-    def _get_weights(self, class_idx: Union[int, List[int]], scores: Tensor, **kwargs: Any) -> List[Tensor]:\n+    def _get_weights(\n+        self, class_idx: Union[int, List[int]], scores: Tensor, eps: float = 1e-8, **kwargs: Any\n+    ) -> List[Tensor]:\n         """Computes the weight coefficients of the hooked activation maps."""\n \n         # Backpropagate\n@@ -168,7 +170,7 @@ def _get_weights(self, class_idx: Union[int, List[int]], scores: Tensor, **kwarg\n         nan_mask = [g2 > 0 for g2 in grad_2]\n         alpha = grad_2\n         for idx, d, mask in zip(range(len(grad_2)), denom, nan_mask):\n-            alpha[idx][mask].div_(d[mask])\n+            alpha[idx][mask].div_(d[mask] + eps)\n \n         # Apply pixel coefficient in each weight\n         return [a.mul_(torch.relu(grad)).flatten(2).sum(-1) for a, grad in zip(alpha, self.hook_g)]\n@@ -256,7 +258,7 @@ def _store_input(self, module: nn.Module, input: Tensor) -> None:\n             self._input = input[0].data.clone()\n \n     def _get_weights(\n-        self, class_idx: Union[int, List[int]], scores: Optional[Tensor] = None, **kwargs: Any\n+        self, class_idx: Union[int, List[int]], scores: Optional[Tensor] = None, eps: float = 1e-8, **kwargs: Any\n     ) -> List[Tensor]:\n         """Computes the weight coefficients of the hooked activation maps."""\n \n@@ -292,7 +294,7 @@ def _get_weights(\n         # Alpha coefficient for each pixel\n         spatial_dims = self.hook_a[0].ndim - 2\n         alpha = [\n-            g2 / (2 * g2 + (g3 * act).flatten(2).sum(-1)[(...,) + (None,) * spatial_dims])\n+            g2 / (2 * g2 + (g3 * act).flatten(2).sum(-1)[(...,) + (None,) * spatial_dims] + eps)\n             for g2, g3, act in zip(grad_2, grad_3, init_fmap)\n         ]\n \n@@ -336,7 +338,9 @@ class XGradCAM(_GradCAM):\n         input_shape: shape of the expected input tensor excluding the batch dimension\n     """\n \n-    def _get_weights(self, class_idx: Union[int, List[int]], scores: Tensor, **kwargs: Any) -> List[Tensor]:\n+    def _get_weights(\n+        self, class_idx: Union[int, List[int]], scores: Tensor, eps: float = 1e-8, **kwargs: Any\n+    ) -> List[Tensor]:\n         """Computes the weight coefficients of the hooked activation maps."""\n \n         # Backpropagate\n@@ -344,7 +348,10 @@ def _get_weights(self, class_idx: Union[int, List[int]], scores: Tensor, **kwarg\n \n         self.hook_a: List[Tensor]  # type: ignore[assignment]\n         self.hook_g: List[Tensor]  # type: ignore[assignment]\n-        return [(grad * act).flatten(2).sum(-1) / act.flatten(2).sum(-1) for act, grad in zip(self.hook_a, self.hook_g)]\n+        return [\n+            (grad * act).flatten(2).sum(-1) / act.flatten(2).sum(-1).add(eps)\n+            for act, grad in zip(self.hook_a, self.hook_g)\n+        ]\n \n \n class LayerCAM(_GradCAM):\n',
            {
                "tests/test_methods_activation.py": 1,
                "tests/test_methods_gradient.py": 1,
                "torchcam/methods/gradient.py": 6,
            },
        ],
        # https://github.com/frgfm/torch-cam/pull/115
        [
            "diff --git a/.flake8 b/.flake8\nindex daef3984..6cd2696b 100644\n--- a/.flake8\n+++ b/.flake8\n@@ -1,4 +1,5 @@\n [flake8]\n max-line-length = 120\n-ignore = F401, E402, E265, F403, W503, W504, F821, W605\n-exclude = .github, .git, venv*, docs, build\n+ignore = E402, E265, F403, W503, W504, E731\n+exclude = .circleci, .git, venv*, docs, build\n+per-file-ignores = **/__init__.py:F401\n",
            {".flake8": 1},
        ],
    ],
)
def test_parse_diff_body(diff_body, expected_parsing):
    out = parse_diff_body(diff_body)
    assert len(out) == len(expected_parsing)
    assert all(len(out[file]) == num_sections for file, num_sections in expected_parsing.items())


@pytest.mark.parametrize(
    "repo_name, pr_num, payload_len, created_at",
    [
        ["frgfm/torch-cam", 115, 11, "2021-11-14T16:12:44Z"],
        ["frgfm/torch-cam", 187, 11, "2022-09-18T17:08:50Z"],
    ],
)
def test_pull_request_get_info(repo_name, pr_num, payload_len, created_at):
    pr = PullRequest(repo_name, pr_num)
    out = pr.get_info()
    assert len(out) == payload_len
    assert out["created_at"] == created_at


@pytest.mark.parametrize(
    "repo_name, pr_num, num_files, num_sections",
    [
        ["frgfm/torch-cam", 115, 1, 1],
        ["frgfm/torch-cam", 187, 3, 8],
    ],
)
def test_pull_request_get_diff(repo_name, pr_num, num_files, num_sections):
    pr = PullRequest(repo_name, pr_num)
    out = pr.get_diff()
    assert len(out) == num_files
    import ipdb

    ipdb.set_trace()
    assert sum(len(sections) for sections in out.values()) == num_sections
