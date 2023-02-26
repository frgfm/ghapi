import pytest

from ghapi.connection import Connection
from ghapi.exceptions import HTTPRequestException
from ghapi.pulls import PullRequest, parse_diff_body, parse_file_diff
from ghapi.repos import Repository


@pytest.mark.parametrize(
    "file_diff, expected_parsing",
    [
        # https://github.com/frgfm/ci-benchmark/pull/15
        [
            'a/dummy_lib/core.py b/dummy_lib/core.py\nindex e52afda..cced706 100644\n--- a/dummy_lib/core.py\n+++ b/dummy_lib/core.py\n@@ -1,12 +1,12 @@\n # Copyright (C) 2022, François-Guillaume Fernandez.\n-\n # This program is licensed under the Apache License 2.0.\n # See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.\n-\n from enum import Enum\n from typing import List\n \n-__all__ = ["greet_contributor", "convert_temperature_sequences", "TemperatureScale"]\n+__all__ = [\n+    "greet_contributor", "convert_temperature_sequences", "TemperatureScale"\n+]\n \n \n class TemperatureScale(Enum):\n@@ -47,9 +47,14 @@ def convert_temperature_sequences(\n     if input_scale == output_scale:\n         return input_temperatures\n \n-    if input_scale == TemperatureScale.FAHRENHEIT and output_scale == TemperatureScale.CELSIUS:\n-        return [(fahrenheit_temp - 32) * 5 / 9 for fahrenheit_temp in input_temperatures]\n-    elif input_scale == TemperatureScale.CELSIUS and output_scale == TemperatureScale.FAHRENHEIT:\n-        return [celsius_temp * 9 / 5 + 32 for celsius_temp in input_temperatures]\n+    if (input_scale == TemperatureScale.FAHRENHEIT\n+            and output_scale == TemperatureScale.CELSIUS):\n+        return [(fahrenheit_temp - 32) * 5 / 9\n+                for fahrenheit_temp in input_temperatures]\n+    elif (input_scale == TemperatureScale.CELSIUS\n+          and output_scale == TemperatureScale.FAHRENHEIT):\n+        return [\n+            celsius_temp * 9 / 5 + 32 for celsius_temp in input_temperatures\n+        ]\n \n     raise NotImplementedError\n'.split(  # noqa: E501
                "\n"
            ),
            [(2, 2, None, None, 6, 6), (5, 5, None, None, 9, 9), (9, 9, 7, 9, 13, 16), (50, 53, 50, 58, 24, 36)],
        ],
        # https://github.com/frgfm/ghapi/pull/27
        [
            'a/tests/fixtures/comment.json b/tests/fixtures/comment.json\nnew file mode 100644\nindex 0000000..f6a7644\n--- /dev/null\n+++ b/tests/fixtures/comment.json\n@@ -0,0 +1 @@\n+{"url":"https://api.github.com/repos/frgfm/ghapi/issues/comments/1366982953"}'.split(  # noqa: E501
                "\n"
            ),
            [(None, None, 1, 1, 6, 6)],
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
        # https://github.com/frgfm/ci-benchmark/pull/15
        [
            'diff --git a/dummy_lib/core.py b/dummy_lib/core.py\nindex e52afda..cced706 100644\n--- a/dummy_lib/core.py\n+++ b/dummy_lib/core.py\n@@ -1,12 +1,12 @@\n # Copyright (C) 2022, François-Guillaume Fernandez.\n-\n # This program is licensed under the Apache License 2.0.\n # See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.\n-\n from enum import Enum\n from typing import List\n \n-__all__ = ["greet_contributor", "convert_temperature_sequences", "TemperatureScale"]\n+__all__ = [\n+    "greet_contributor", "convert_temperature_sequences", "TemperatureScale"\n+]\n \n \n class TemperatureScale(Enum):\n@@ -47,9 +47,14 @@ def convert_temperature_sequences(\n     if input_scale == output_scale:\n         return input_temperatures\n \n-    if input_scale == TemperatureScale.FAHRENHEIT and output_scale == TemperatureScale.CELSIUS:\n-        return [(fahrenheit_temp - 32) * 5 / 9 for fahrenheit_temp in input_temperatures]\n-    elif input_scale == TemperatureScale.CELSIUS and output_scale == TemperatureScale.FAHRENHEIT:\n-        return [celsius_temp * 9 / 5 + 32 for celsius_temp in input_temperatures]\n+    if (input_scale == TemperatureScale.FAHRENHEIT\n+            and output_scale == TemperatureScale.CELSIUS):\n+        return [(fahrenheit_temp - 32) * 5 / 9\n+                for fahrenheit_temp in input_temperatures]\n+    elif (input_scale == TemperatureScale.CELSIUS\n+          and output_scale == TemperatureScale.FAHRENHEIT):\n+        return [\n+            celsius_temp * 9 / 5 + 32 for celsius_temp in input_temperatures\n+        ]\n \n     raise NotImplementedError\ndiff --git a/tests/test_core.py b/tests/test_core.py\nindex 90d3940..cdecb87 100644\n--- a/tests/test_core.py\n+++ b/tests/test_core.py\n@@ -1,6 +1,8 @@\n import pytest\n \n-from dummy_lib.core import TemperatureScale, convert_temperature_sequences, greet_contributor\n+from dummy_lib.core import convert_temperature_sequences\n+from dummy_lib.core import greet_contributor\n+from dummy_lib.core import TemperatureScale\n \n \n @pytest.mark.parametrize(\n@@ -44,10 +46,13 @@ def test_greet_contributor(name, expected_output):\n             [10, -10.0, 0],\n         ],\n         # Error\n-        [[10, -10.0, 0], TemperatureScale.CELSIUS, "kelvin", NotImplementedError, None],\n+        [[10, -10.0, 0], TemperatureScale.CELSIUS, "kelvin",\n+         NotImplementedError, None],\n     ],\n )\n-def test_convert_temperature_sequences(input_temperatures, input_scale, output_scale, error_type, expected_output):\n+def test_convert_temperature_sequences(input_temperatures, input_scale,\n+                                       output_scale, error_type,\n+                                       expected_output):\n     kwargs = {}\n     if input_scale is not None:\n         kwargs["input_scale"] = input_scale\n@@ -55,7 +60,8 @@ def test_convert_temperature_sequences(input_temperatures, input_scale, output_s\n         kwargs["output_scale"] = output_scale\n \n     if error_type is None:\n-        assert convert_temperature_sequences(input_temperatures, **kwargs) == expected_output\n+        assert (convert_temperature_sequences(input_temperatures,\n+                                              **kwargs) == expected_output)\n     else:\n         with pytest.raises(error_type):\n             convert_temperature_sequences(input_temperatures, **kwargs)\n',  # noqa: E501
            {"dummy_lib/core.py": 4, "tests/test_core.py": 4},
        ],
        # https://github.com/frgfm/ghapi/pull/17
        [
            'diff --git a/.conda/meta.yaml b/.conda/meta.yaml\nnew file mode 100644\nindex 0000000..fbd6acb\n--- /dev/null\n+++ b/.conda/meta.yaml\n@@ -0,0 +1,49 @@\n+# https://docs.conda.io/projects/conda-build/en/latest/resources/define-metadata.html#loading-data-from-other-files\n+# https://github.com/conda/conda-build/pull/4480\n+# for conda-build > 3.21.9\n+# {% set pyproject = load_file_data(\'../pyproject.toml\', from_recipe_dir=True) %}\n+# {% set project = pyproject.get(\'project\') %}\n+# {% set urls = pyproject.get(\'project\', {}).get(\'urls\') %}\n+{% set name = "ghapi-client" %}\n+\n+package:\n+  name: {{ name|lower }}\n+  version: "{{ environ.get(\'BUILD_VERSION\') }}"\n+\n+source:\n+  fn: {{ name }}-{{ environ.get(\'BUILD_VERSION\') }}.tar.gz\n+  url: ../dist/{{ name }}-{{ environ.get(\'BUILD_VERSION\') }}.tar.gz\n+\n+build:\n+  number: 0\n+  noarch: python\n+  script: {{ PYTHON }} setup.py install --single-version-externally-managed --record=record.txt\n+\n+requirements:\n+  host:\n+    - python\n+    - pip\n+    - setuptools\n+    - wheel\n+  run:\n+    - python >=3.6,<4.0\n+    - requests >=2.24.0,<3.0.0\n+\n+test:\n+  imports:\n+    - ghapi\n+  requires:\n+    - pip\n+  commands:\n+    - pip check\n+\n+about:\n+  home: https://github.com/frgfm/ghapi\n+  license: Apache-2.0\n+  license_family: Apache\n+  license_file: LICENSE\n+  summary: \'Python client for the GitHub API\'\n+  # description: |\n+  #   {{ data[\'long_description\'] | replace("\\n", "\\n    ") | replace("#", \'\\#\')}}\n+  doc_url: https://frgfm.github.io/ghapi\n+  dev_url: https://github.com/frgfm/ghapi\ndiff --git a/.github/collect_env.py b/.github/collect_env.py\nindex f3824c5..6c8b603 100644\n--- a/.github/collect_env.py\n+++ b/.github/collect_env.py\n@@ -168,12 +168,6 @@ def replace_bools(dct, true="Yes", false="No"):\n                 dct[key] = false\n         return dct\n \n-    def maybe_start_on_next_line(string):\n-        # If `string` is multiline, prepend a \\n to it.\n-        if string is not None and len(string.split("\\n")) > 1:\n-            return "\\n{}\\n".format(string)\n-        return string\n-\n     mutable_dict = envinfo._asdict()\n \n     # Replace True with Yes, False with No\ndiff --git a/.github/workflows/release.yml b/.github/workflows/release.yml\nindex bc72dae..800159a 100644\n--- a/.github/workflows/release.yml\n+++ b/.github/workflows/release.yml\n@@ -78,7 +78,7 @@ jobs:\n         run: |\n           python setup.py sdist\n           mkdir conda-dist\n-          conda-build .conda/ -c pytorch --output-folder conda-dist\n+          conda-build .conda/ --output-folder conda-dist\n           ls -l conda-dist/noarch/*tar.bz2\n           anaconda upload conda-dist/noarch/*tar.bz2 -u frgfm\n \n@@ -95,5 +95,5 @@ jobs:\n           auto-activate-base: true\n       - name: Install package\n         run: |\n-          conda install -c frgfm ghapi\n+          conda install -c frgfm ghapi-client\n           python -c "import ghapi; print(ghapi.__version__)"\ndiff --git a/.gitignore b/.gitignore\nindex 742c638..700bd0f 100644\n--- a/.gitignore\n+++ b/.gitignore\n@@ -128,3 +128,5 @@ dmypy.json\n # Pyre type checker\n .pyre/\n ghapi/version.py\n+conda-dist/\n+dist/\ndiff --git a/.pre-commit-config.yaml b/.pre-commit-config.yaml\nindex b615adc..b1667e6 100644\n--- a/.pre-commit-config.yaml\n+++ b/.pre-commit-config.yaml\n@@ -3,6 +3,7 @@ repos:\n     rev: v4.3.0\n     hooks:\n       - id: check-yaml\n+        exclude: .conda\n       - id: check-toml\n       - id: end-of-file-fixer\n       - id: trailing-whitespace\ndiff --git a/README.md b/README.md\nindex 1b56f58..826c1d9 100644\n--- a/README.md\n+++ b/README.md\n@@ -16,10 +16,17 @@\n   <a href="https://github.com/PyCQA/bandit">\n     <img src="https://img.shields.io/badge/security-bandit-yellow.svg?style=flat-square" alt="bandit">\n   </a>\n+  <a href="https://www.codacy.com/gh/frgfm/ghapi/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=frgfm/ghapi&amp;utm_campaign=Badge_Grade"><img src="https://app.codacy.com/project/badge/Grade/c332510e1ed24026a9479edf1199d2e2"/></a>\n </p>\n <p align="center">\n-  <img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/frgfm/ghapi">\n-  <img alt="GitHub" src="https://img.shields.io/github/license/frgfm/ghapi">\n+  <a href="https://pypi.org/project/ghapi-client/">\n+    <img src="https://img.shields.io/pypi/v/ghapi-client.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPi Status">\n+  </a>\n+  <a href="https://anaconda.org/frgfm/ghapi-client">\n+    <img alt="Anaconda" src="https://img.shields.io/conda/vn/frgfm/ghapi-client?style=flat-square?style=flat-square&logo=Anaconda&logoColor=white&label=conda">\n+  </a>\n+  <img src="https://img.shields.io/pypi/pyversions/ghapi-client.svg?style=flat-square" alt="pyversions">\n+  <img src="https://img.shields.io/pypi/l/ghapi-client.svg?style=flat-square" alt="license">\n </p>\n \n \ndiff --git a/docs/source/changelog.rst b/docs/source/changelog.rst\nindex f97d3e4..a2df95f 100644\n--- a/docs/source/changelog.rst\n+++ b/docs/source/changelog.rst\n@@ -1,6 +1,6 @@\n Changelog\n =========\n \n-v0.1.0 (?)\n+v0.1.0 (2022-12-26)\n -------------------\n Release note: `v0.1.0 <https://github.com/frgfm/ghapi/releases/tag/v0.1.0>`_\ndiff --git a/setup.py b/setup.py\nindex 283a68a..0ab0f24 100644\n--- a/setup.py\n+++ b/setup.py\n@@ -10,7 +10,7 @@\n from setuptools import setup\n \n PKG_INDEX = "ghapi-client"\n-VERSION = os.getenv("BUILD_VERSION", "0.1.0.dev0")\n+VERSION = os.getenv("BUILD_VERSION", "0.1.1.dev0")\n \n \n if __name__ == "__main__":\n',  # noqa: E501
            {
                ".conda/meta.yaml": 1,
                ".github/collect_env.py": 1,
                ".github/workflows/release.yml": 2,
                ".gitignore": 1,
                ".pre-commit-config.yaml": 1,
                "README.md": 2,
                "docs/source/changelog.rst": 1,
                "setup.py": 1,
            },
        ],
    ],
)
def test_parse_diff_body(diff_body, expected_parsing):
    out = parse_diff_body(diff_body)
    assert len(out) == len(expected_parsing)
    for file, num_sections in expected_parsing.items():
        assert len(out[file]) == num_sections


def test_pull_request_get_info(mock_pull):
    conn = Connection(url="https://www.github.com")
    pr = PullRequest(Repository("frgfm", "ghapi", conn), 27)
    # Wrong api url
    with pytest.raises(HTTPRequestException):
        pr.get_info()
    # Fix url
    pr.conn.url = "https://api.github.com"
    # Set response
    pr._info = mock_pull
    out = pr.get_info()
    assert len(out) == 16
    assert out["created_at"] == "2022-12-29T17:03:13Z"


def test_pull_request_get_diff(mock_pull_diff):
    conn = Connection(url="https://www.github.com")
    pr = PullRequest(Repository("frgfm", "ghapi", conn), 15)
    # Wrong api url
    with pytest.raises(HTTPRequestException):
        pr.get_diff()
    # Fix url
    pr.conn.url = "https://api.github.com"
    # Set response
    pr._diff = mock_pull_diff
    out = pr.get_diff()
    # num of files
    assert len(out) == 1
    # num of modification blocks
    assert sum(len(sections) for sections in out.values()) == 2


def test_pull_request_list_comments(mock_comment):
    conn = Connection(url="https://www.github.com")
    pr = PullRequest(Repository("frgfm", "ghapi", conn), 27)
    # Wrong api url
    with pytest.raises(HTTPRequestException):
        pr.list_comments()
    # Fix url
    pr.conn.url = "https://api.github.com"
    # Set response
    pr._comments = [mock_comment]
    out = pr.list_comments()
    assert len(out) == 1 and isinstance(out[0], dict) and len(out[0]) == 6


def test_pull_request_list_review_comments(mock_comment):
    conn = Connection(url="https://www.github.com")
    pr = PullRequest(Repository("frgfm", "ghapi", conn), 27)
    # Wrong api url
    with pytest.raises(HTTPRequestException):
        pr.list_review_comments()
    # Fix url
    pr.conn.url = "https://api.github.com"
    # Set response
    pr._review_comments = [mock_comment]
    out = pr.list_review_comments()
    assert len(out) == 1 and isinstance(out[0], dict) and len(out[0]) == 6


def test_pull_request_list_reviews(mock_review):
    conn = Connection(url="https://www.github.com")
    pr = PullRequest(Repository("frgfm", "Holocron", conn), 260)
    # Wrong api url
    with pytest.raises(HTTPRequestException):
        pr.list_reviews()
    # Fix url
    pr.conn.url = "https://api.github.com"
    # Set response
    pr._comments = [mock_review]
    out = pr.list_reviews()
    assert len(out) == 1 and isinstance(out[0], dict) and len(out[0]) == 6


def test_pull_request_list_files():
    conn = Connection(url="https://www.github.com")
    pr = PullRequest(Repository("frgfm", "Holocron", conn), 260)
    # Wrong api url
    with pytest.raises(HTTPRequestException):
        pr.list_files()
    # Fix url
    pr.conn.url = "https://api.github.com"
    # Set response
    out = pr.list_files()
    assert out.keys() == {"api/poetry.lock"}
