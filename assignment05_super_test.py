"""
CS3B, Assignment #5, Logic gate simulation (Part 2)
Copyright 2020 Zibin Yang
Instructor's solution for testing

Modified to demonstrate proper use of super() in multiple inheritance
"""

import itertools
import unittest
from assignment05_super import *


class MockGate(LogicGate):
    """
    A gate used for testing
    """

    def __init__(self, name):
        self.evaluate_called = False

    def evaluate(self):
        # In this mock version is doesn't set the output
        self.evaluate_called = True


class MockInput(Input):
    """
    Input used for testing
    """

    # Hmm, good reason not to call parent's __init__(): this is just a mock!
    def __init__(self):
        pass

    # Override Input.value for testing
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # In this mock version it doesn't ask the owner to evaluate
        self._value = value


class InputTest(unittest.TestCase):
    def setUp(self):
        self.mock_gate = MockGate("mock")
        self.input = Input(self.mock_gate)

    def testInit(self):
        self.assertIs(self.mock_gate, self.input.owner)
        self.assertTrue(not hasattr(self.input, "value") or self.input.value is None)
        self.assertTrue(not hasattr(self.input, "_value") or self.input._value is None)

    def testInitFailure(self):
        with self.assertRaises(Exception):
            input0 = Input("bad owner")

    def testStr(self):
        # Make sure __str__ can handle no value being set
        self.assertEqual(str, type(self.input.__str__()))

    def testValueGetterSetter(self):
        self.input.value = True
        self.assertTrue(self.input.value)

        self.input.value = False
        self.assertFalse(self.input.value)

    def testValueSetterNormalizeToBool(self):
        self.input.value = 1
        self.assertTrue(self.input.value)

        self.input.value = ""
        self.assertFalse(self.input.value)

    def testValueSetterCallOwnerEvaluate(self):
        self.input.value = True
        self.assertTrue(self.input.owner.evaluate_called, "Setting input value didn't call owner's evaluate")


class OutputTest(unittest.TestCase):
    def setUp(self):
        self.output = Output()

    def testInit(self):
        self.assertTrue(not hasattr(self.output, "value") or self.output.value is None)
        self.assertTrue(not hasattr(self.output, "_value") or self.output._value is None)

    def testStr(self):
        # Make sure __str__ can handle no value being set
        self.assertEqual(str, type(self.output.__str__()))

    def testValueGetterSetter(self):
        self.output.value = True
        self.assertTrue(self.output.value)

        self.output.value = False
        self.assertFalse(self.output.value)

    def testConnect(self):
        input0 = MockInput()
        input1 = MockInput()

        self.output.connect(input0)
        self.assertTrue(input0 in self.output.connections, "Output should put input0 in its connections")

        self.output.connect(input1)
        self.assertTrue(input0 in self.output.connections, "Output should still have input0 in its connections")
        self.assertTrue(input1 in self.output.connections, "Output should put input1 in its connections")

    def testConnectFailure1(self):
        with self.assertRaises(TypeError):
            self.output.connections("bad input")

    def testConnectFailure2(self):
        input0 = MockInput()
        self.output.connect(input0)
        self.output.connect(input0)
        self.assertEqual(1, self.output.connections.count(input0))

    def testValueSetterSetInputValue1(self):
        # Test the sequence: set-value, connect
        input0 = MockInput()
        input1 = MockInput()

        self.output.value = True
        self.output.connect(input0)
        self.output.connect(input1)
        self.assertTrue(input0.value)
        self.assertTrue(input1.value)

    def testValueSetterSetInputValue2(self):
        # Test the sequence: connect, set-value
        input0 = MockInput()
        input1 = MockInput()

        # If the implementation doesn't handle when output.value isn't set, this might raise an exception
        self.output.connect(input0)
        self.output.connect(input1)

        self.output.value = True

        self.assertTrue(input0.value)
        self.assertTrue(input1.value)


class LogicGateTest(unittest.TestCase):
    def setUp(self):
        self.binary_gate_types_map = {
            AndGate: lambda a, b: a and b,
            OrGate: lambda a, b: a or b,
            XorGate: lambda a, b: a != b,
        }

        self.binary_gate_types = self.binary_gate_types_map.keys()

        self.gate_types = list(self.binary_gate_types) + [NotGate]

        self.input_values = [True, False]

    def testName(self):
        name = "not"
        not_gate = NotGate(name)
        self.assertEqual(name, not_gate.name)

    def testSetNameInputOutput(self):
        not_gate = NotGate("not")

        with self.assertRaises(Exception):
            not_gate.name = "not possible"

        with self.assertRaises(Exception):
            not_gate.input = "not possible"

        with self.assertRaises(Exception):
            not_gate.output = "not possible"

    def testStr(self):
        for gate_type in self.gate_types:
            self.assertEqual(str, type(gate_type(gate_type.__name__).__str__()))

    def testNotGateOutputNotSet(self):
        # If implementation chooses to set value upon initialization, it should be None
        not_gate = NotGate("not")
        if hasattr(not_gate.output, "value"):
            self.assertIsNone(not_gate.output.value)

    def testNotGate(self):
        not_gate = NotGate("not")
        for i in [False, True]:
            not_gate.input.value = i
            self.assertEqual(not i, not_gate.output.value)

    def testBinaryGateOutputNotSet(self):
        # If implementation chooses to set value upon initialization, it should be None
        for gate_type in self.binary_gate_types:
            with self.subTest(f"Testing {gate_type.__name__}"):
                gate = gate_type(gate_type.__name__)
                if hasattr(gate.output, "value"):
                    self.assertIsNone(gate.output.value)

                    gate.input0.value = True
                    self.assertIsNone(gate.output.value)

    def testBinaryGate(self):
        for gate_type, op in self.binary_gate_types_map.items():
            with self.subTest(f"Testing {gate_type.__name__}"):
                gate = gate_type(gate_type.__name__)
                for a in self.input_values:
                    for b in self.input_values:
                        gate.input0.value = a
                        gate.input1.value = b
                        self.assertEqual(op(a, b), gate.output.value,
                                         f"{a} {gate_type.__name__} {b} = {gate.output.value}")

    def testNotNot(self):
        not_gate1 = NotGate("not1")
        not_gate2 = NotGate("not2")
        not_gate1.output.connect(not_gate2.input)

        for i in self.input_values:
            not_gate1.input.value = i
            self.assertEqual(i, not_gate2.output.value)

    def testAndNot(self):
        and_gate = AndGate("and")
        not_gate = NotGate("not")
        and_gate.output.connect(not_gate.input)

        for a in self.input_values:
            for b in self.input_values:
                and_gate.input0.value = a
                and_gate.input1.value = b
                self.assertEqual(not (a and b), not_gate.output.value)


#####################################################################
# New for Assignment #5
#####################################################################

class AbstractLogicGateTest(unittest.TestCase):
    def testAbc(self):
        with self.assertRaises(Exception):
            LogicGate("abc, cannot instantiate")

    def testAbstractMethod(self):
        self.assertTrue("evaluate" in LogicGate.__abstractmethods__)


# These attributes are not required for the assignment, but it's good to have them for testing.
# if not hasattr(UnaryGate, "NUMBER_OF_COMPONENTS"):
#     UnaryGate.NUMBER_OF_COMPONENTS = 2
# if not hasattr(BinaryGate, "NUMBER_OF_COMPONENTS"):
#     BinaryGate.NUMBER_OF_COMPONENTS = 3

unary_gate_cost = 10 * (2 ** 2)
binary_gate_cost = 10 * (3 ** 2)


def calc_cost(multiplier, number_of_components):
    return multiplier * number_of_components ** 2


class CostMixinTest(unittest.TestCase):
    def testNumberOfComponents(self):
        number_of_components = 9
        cost_calculator = CostMixin(number_of_components)
        self.assertEqual(number_of_components, cost_calculator.number_of_components)

    def testCost(self):
        number_of_components = 9
        cost_calculator = CostMixin(number_of_components)
        self.assertEqual(calc_cost(CostMixin.COST_MULTIPLIER, number_of_components), cost_calculator.cost)

    def testUnaryGateCost(self):
        self.assertEqual(unary_gate_cost, NotGate("not").cost)

    def testBinaryGateCost(self):
        self.assertEqual(binary_gate_cost, AndGate("and").cost)
        self.assertEqual(binary_gate_cost, OrGate("or").cost)
        self.assertEqual(binary_gate_cost, XorGate("xor").cost)


class NodeMixinTest(unittest.TestCase):
    def testNextGetterBasic(self):
        node = NodeMixin()
        self.assertIsNone(node.next)

    def testNextGetter(self):
        node = NodeMixin()
        next_node = NodeMixin()
        node.next = next_node
        self.assertIs(next_node, node.next)

    def testNodeNextSetterValid(self):
        # Create a child class of NodeMixin, which should be allowed to be set to .next
        class NodeMixinChild(NodeMixin): pass

        node = NodeMixin()
        node_child = NodeMixinChild()
        node.next = node_child
        self.assertIs(node_child, node.next)

    def testNodeNextSetterInvalid(self):
        with self.assertRaises(TypeError):
            NodeMixin().next = "bad next"


class CircuitTest(unittest.TestCase):
    def setUp(self):
        self.circuit = Circuit()

    def testBasic(self):
        # There's not much to check, but just the fact that circuit.add doesn't raise
        # an exception is good news.
        self.circuit.add(NotGate("not"))

    def testBasicFailure(self):
        with self.assertRaises(TypeError):
            self.circuit.add("bad gate")

    def testNoGate(self):
        # Empty circuit should have 0 cost
        self.assertEqual(0, self.circuit.cost)

    def testSingleGate1(self):
        # circuit with a single not gate should have the same cost as a not gate
        not_gate = NotGate("not", self.circuit)
        self.assertEqual(unary_gate_cost, self.circuit.cost)

    def testSingleGate2(self):
        and_gate = AndGate("and", self.circuit)
        self.assertEqual(binary_gate_cost, self.circuit.cost)

    def testNotNotCircuit(self):
        not_gate1 = NotGate("not1", self.circuit)
        not_gate2 = NotGate("not2", self.circuit)
        not_gate1.output.connect(not_gate2.input)
        # Do it twice to catch implementation that use an instance attribute to
        # add up the costs
        self.assertEqual(unary_gate_cost * 2, self.circuit.cost,
                         "Cost of NOT-NOT circuit is " + str(self.circuit.cost))
        self.assertEqual(unary_gate_cost * 2, self.circuit.cost,
                         "Cost of NOT-NOT circuit is " + str(self.circuit.cost))

    def testAndNotCircuit(self):
        not_gate = NotGate("not", self.circuit)
        and_gate = AndGate("and", self.circuit)
        self.assertEqual(unary_gate_cost + binary_gate_cost, self.circuit.cost)
        self.assertEqual(unary_gate_cost + binary_gate_cost, self.circuit.cost)

    def testMultipleGates(self):
        # circuit with one unary gate and two binary gates
        not_gate = NotGate("not", self.circuit)
        and_gate = AndGate("and", self.circuit)
        or_gate = OrGate("or", self.circuit)
        self.assertEqual(unary_gate_cost + binary_gate_cost * 2, self.circuit.cost)
        self.assertEqual(unary_gate_cost + binary_gate_cost * 2, self.circuit.cost)


class FullAdderTest(unittest.TestCase):
    def testFullAdder(self):
        bool_list = [False, True]
        for a, b, ci in itertools.product(bool_list, bool_list, bool_list):
            with self.subTest(f"{a}, {b}, {ci}"):
                s, co, cost = full_adder(a, b, ci)

                expected_s = a ^ b ^ ci
                expected_co = (a and b) or (a and ci) or (b and ci)
                expected_cost = binary_gate_cost * 5

                self.assertEqual(expected_s, s)
                self.assertEqual(expected_co, co)
                self.assertEqual(expected_cost, cost)


class LayoutMixinTestCase(unittest.TestCase):
    def testNotGate(self):
        not_gate = NotGate("not", x=28, y=99)
        self.assertEqual(not_gate.x, 28)
        self.assertEqual(not_gate.y, 99)

    def testAndGate(self):
        and_gate = AndGate("and", x=500, y=1000)
        self.assertEqual(and_gate.x, 500)
        self.assertEqual(and_gate.y, 1000)




if __name__ == "__main__":
    unittest.main()
