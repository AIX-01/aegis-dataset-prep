from __future__ import annotations

import json
import pathlib
import ast
import unittest


NOTEBOOK = pathlib.Path("Qwen3-VL-2B-Finetuning-Eval.ipynb")


class NotebookCleanTests(unittest.TestCase):
    def test_notebook_has_no_committed_outputs_or_execution_counts(self) -> None:
        notebook = json.loads(NOTEBOOK.read_text())
        dirty_cells = []
        for index, cell in enumerate(notebook.get("cells", []), start=1):
            if cell.get("cell_type") != "code":
                continue
            if cell.get("outputs"):
                dirty_cells.append(f"cell {index}에 output이 남아 있습니다")
            if cell.get("execution_count") is not None:
                dirty_cells.append(f"cell {index}에 execution_count가 남아 있습니다")

        self.assertEqual(dirty_cells, [])

    def test_notebook_code_cells_parse_as_python(self) -> None:
        notebook = json.loads(NOTEBOOK.read_text())
        syntax_errors = []
        for index, cell in enumerate(notebook.get("cells", []), start=1):
            if cell.get("cell_type") != "code":
                continue
            source = "".join(cell.get("source", []))
            try:
                ast.parse(source)
            except SyntaxError as exc:
                syntax_errors.append(f"cell {index}: {exc.msg}")

        self.assertEqual(syntax_errors, [])


if __name__ == "__main__":
    unittest.main()
