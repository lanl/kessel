from kessel.workflow import load_workflow_from_string
from kessel.context import Context


class MockShellEnvironment:
    pass


def test_variable_reference():
    ctx = Context(MockShellEnvironment())
    workflow = load_workflow_from_string("""
variables:
   b: value
   a: $b
                                  """)
    variables = {}
    for k, v in workflow["variables"].items():
        variables[k] = ctx.evaluate(v, [variables])

    assert variables["a"] == "value"
    assert variables["b"] == "value"
