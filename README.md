# Python client for GitHub API

<p align="center">
  <a href="https://github.com/frgfm/ghapi/actions?query=workflow%3Abuilds">
    <img alt="CI Status" src="https://img.shields.io/github/actions/workflow/status/frgfm/ghapi/builds.yml?branch=main&label=CI&logo=github&style=flat-square">
  </a>
  <a href="https://frgfm.github.io/ghapi">
    <img alt="Documentation Status" src="https://img.shields.io/github/actions/workflow/status/frgfm/ghapi/docs.yaml?branch=main&label=docs&logo=read-the-docs&style=flat-square">
  </a>
  <a href="https://codecov.io/gh/frgfm/ghapi">
    <img src="https://codecov.io/gh/frgfm/ghapi/branch/main/graph/badge.svg?token=ISgEpF7y0A" alt="Test coverage percentage">
  </a>
  <a href="https://github.com/ambv/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="black">
  </a>
  <a href="https://github.com/PyCQA/bandit">
    <img src="https://img.shields.io/badge/security-bandit-yellow.svg?style=flat-square" alt="bandit">
  </a>
</p>
<p align="center">
  <img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/frgfm/ghapi">
  <img alt="GitHub" src="https://img.shields.io/github/license/frgfm/ghapi">
</p>


## Quick Tour

### Interacting with Pull Request

This project uses [GitHub API](https://docs.github.com/en/rest) to fetch information from GitHub using a Python wrapper.

You can find the exhaustive list of supported features in the [documentation](https://frgfm.github.io/ghapi). For instance, you can retrieve basic information about your pull request as follows:

```python
from ghapi.pulls import Repository, PullRequest

pr = PullRequest(Repository("frgfm", "torch-cam"), 187)
# Get the PR information
pr.get_info()
```
```
{'title': 'fix: Fixed zero division for weight computation in gradient based methods',
 'created_at': '2022-09-18T17:08:50Z',
 'description': 'This PR introduces an `eps` to all divisions in gradient methods to avoid NaNs.\r\n\r\nCloses #186',
 'labels': [{'id': 1929545961,
   'node_id': 'MDU6TGFiZWwxOTI5NTQ1OTYx',
   'url': 'https://api.github.com/repos/frgfm/torch-cam/labels/type:%20bug',
   'name': 'type: bug',
   'color': 'd73a4a',
   'default': False,
   'description': "Something isn't working"},
  {'id': 1929975543,
   'node_id': 'MDU6TGFiZWwxOTI5OTc1NTQz',
   'url': 'https://api.github.com/repos/frgfm/torch-cam/labels/ext:%20tests',
   'name': 'ext: tests',
   'color': 'f7e101',
   'default': False,
   'description': 'Related to test'},
  {'id': 1929975788,
   'node_id': 'MDU6TGFiZWwxOTI5OTc1Nzg4',
   'url': 'https://api.github.com/repos/frgfm/torch-cam/labels/module:%20methods',
   'name': 'module: methods',
   'color': 'f7e101',
   'default': False,
   'description': 'Related to torchcam.methods'}],
 'user': 'frgfm',
 'mergeable': None,
 'changed_files': 3,
 'additions': 15,
 'deletions': 8,
 'base': {'branch': 'main', 'sha': '0a5e06051440e27de6027ec382517a2c71686298'},
 'head': {'repo': 'frgfm/torch-cam',
  'branch': 'grad-nans',
  'sha': 'd49f4a3d847e130e99c3d20311e1450f074fd29f'}}
```

If you're interested in reviewing the pull request, you might be interested in the code diff:
```python
# Retrieve the code diff
full_diff = pr.get_diff()
# Print the first diff section
print("\n".join(full_diff["torchcam/methods/gradient.py"][0]))
```

```
@@ -149,7 +149,9 @@ class GradCAMpp(_GradCAM):
         input_shape: shape of the expected input tensor excluding the batch dimension
     """

-    def _get_weights(self, class_idx: Union[int, List[int]], scores: Tensor, **kwargs: Any) -> List[Tensor]:
+    def _get_weights(
+        self, class_idx: Union[int, List[int]], scores: Tensor, eps: float = 1e-8, **kwargs: Any
+    ) -> List[Tensor]:
         """Computes the weight coefficients of the hooked activation maps."""

         # Backpropagate
```


## Setup

Python 3.6 (or higher) and [pip](https://pip.pypa.io/en/stable/)/[conda](https://docs.conda.io/en/latest/miniconda.html) are required to install `ghapi`.

### Developer installation

Alternatively, if you wish to use the latest features of the project that haven't made their way to a release yet, you can install the package from source:

```shell
git clone https://github.com/frgfm/ghapi.git
pip install -e ghapi/.
```

## What else

### Documentation

The full package documentation is available [here](https://frgfm.github.io/ghapi/) for detailed specifications.


## Contributing

Feeling like extending the range of supported API feature? Or perhaps submitting a new feature idea? Any sort of contribution is greatly appreciated!

You can find a short guide in [`CONTRIBUTING`](CONTRIBUTING.md) to help grow this project!



## License

Distributed under the Apache 2.0 License. See [`LICENSE`](LICENSE) for more information.
