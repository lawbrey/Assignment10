"""
CS3B, Assignment #5, Logic gate simulation (Part 2)
"""

# New for Assginment #5
from abc import ABC, abstractmethod


class LayoutMixin:
    def __init__(self, x=None, y=None, **kwargs):
        self.x = x
        self.y = y
        super().__init__(**kwargs)


class Input:
    def __init__(self, owner):
        if not isinstance(owner, LogicGate):
            raise Exception("Owner should be a type of LogicGate")
        self._owner = owner

    def __str__(self):
        try:
            return str(self.value)
        except AttributeError:
            # It's possible to not have a value at the beginning
            return "(no value)"

    @property
    def owner(self):
        return self._owner

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # Normalize the value to bool
        self._value = bool(value)
        # Now that the input value has changed, tell to owner logic gate to re-evaluate
        self._owner.evaluate()


class Output:
    def __init__(self):
        self._connections = []

    def __str__(self):
        try:
            return str(self.value)
        except AttributeError:
            # It's possible not to have a value at the beginning
            return "(no value)"

    def connect(self, input):
        if not isinstance(input, Input):
            raise Exception("Output must be connected to an input")
        if input not in self._connections:
            self._connections.append(input)
        try:
            input.value = self._value
        except AttributeError:
            # If self.value is not there, skip it
            pass

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # Normalize the value to bool
        self._value = bool(value)
        # After the output value changes, remember to send it to all the connected inputs
        for connection in self._connections:
            connection.value = self.value

    @property
    def connections(self):
        return self._connections


# New for Assginment #5
class CostMixin:
    COST_MULTIPLIER = 10

    def __init__(self, number_of_components, **kwargs):
        super().__init__(**kwargs)
        self._number_of_components = number_of_components
        self._cost = self.COST_MULTIPLIER * (self.number_of_components ** 2)

    @property
    def number_of_components(self):
        return self._number_of_components

    @property
    def cost(self):
        return self._cost


# New for Assginment #5
class NodeMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.next = None

    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, next):
        # Allow next to be set to None, in addition to NodeMixin
        if (next is not None) and (not isinstance(next, NodeMixin)):
            raise TypeError("next should be a NodeMixin")
        self._next = next


# New for Assginment #5
class Circuit:
    # Not allowed to use Python list of any list library; must use own linked list implementation
    def __init__(self):
        self._front = None

    def add(self, gate):
        if not (isinstance(gate, LogicGate) and isinstance(gate, NodeMixin)):
            raise TypeError("Only LogicGate as a NodeMixin is allowed to be added to the circuit")
        gate.next = self._front
        self._front = gate

    @property
    def cost(self):
        total_cost = 0
        gate = self._front
        while gate is not None:
            total_cost += gate.cost
            gate = gate.next
        return total_cost


# New for Assginment #5
class LogicGate(ABC, LayoutMixin, NodeMixin, CostMixin):
    def __init__(self, name, circuit=None, **kwargs):
        super().__init__(**kwargs)  # New for Assginment #5, calling NodeMixin.__init__()
        if circuit is not None:
            circuit.add(self)
        self._name = name

    @property
    def name(self):
        return self._name

    @abstractmethod
    def evaluate(self):
        pass


# New for Assginment #5
class UnaryGate(LogicGate):
    NUMBER_OF_COMPONENTS = 2  # 1 input and 1 output

    def __init__(self, name, circuit=None, **kwargs):
        super().__init__(name=name,
                         circuit=circuit,
                         number_of_components=self.NUMBER_OF_COMPONENTS,
                         **kwargs)
        self._input = Input(self)
        self._output = Output()

    def __str__(self):
        return f"Gate {self.name}: input={self.input}, output={self.output}"

    @property
    def input(self):
        return self._input

    @property
    def output(self):
        return self._output


# New for Assginment #5
class BinaryGate(LogicGate):
    NUMBER_OF_COMPONENTS = 3  # 2 inputs and 1 output

    def __init__(self, name, circuit=None, **kwargs):
        super().__init__(name=name,
                         circuit=circuit,
                         number_of_components=self.NUMBER_OF_COMPONENTS,
                         **kwargs)
        self._input0 = Input(self)
        self._input1 = Input(self)
        self._output = Output()

    def __str__(self):
        return f"Gate {self.name}: input0={self.input0}, input1={self.input1}, output={self.output}"

    @property
    def input0(self):
        return self._input0

    @property
    def input1(self):
        return self._input1

    @property
    def output(self):
        return self._output


class NotGate(UnaryGate):
    def evaluate(self):
        self.output.value = not self.input.value


class AndGate(BinaryGate):
    def evaluate(self):
        try:
            # This may throw an exception, if one of the input is not yet set, which is possible
            # in the normal course of evaluation, because setting the first input will kick
            # off the evaluation.  So just don't set the output.
            self.output.value = self.input0.value and self.input1.value
        except AttributeError:
            pass


class OrGate(BinaryGate):
    def evaluate(self):
        try:
            self.output.value = self.input0.value or self.input1.value
        except AttributeError:
            pass


class XorGate(BinaryGate):
    def evaluate(self):
        try:
            # Assume the value is bool, != is same as xor
            self.output.value = (self.input0.value != self.input1.value)
        except AttributeError:
            pass


def test():
    tests = [test_not, test_and, test_or, test_xor, test_not_not, test_and_not]
    for t in tests:
        print("Running " + t.__name__ + " " + "-" * 20)
        t()


def test_not():
    not_gate = NotGate("not")
    not_gate.input.value = True
    print(not_gate)
    not_gate.input.value = False
    print(not_gate)


def test_and():
    and_gate = AndGate("and")
    print("AND gate initial state:", and_gate)
    and_gate.input0.value = True
    print("AND gate with 1 input set", and_gate)
    and_gate.input1.value = False
    print("AND gate with 2 inputs set:", and_gate)
    and_gate.input1.value = True
    print("AND gate with 2 inputs set:", and_gate)


def test_or():
    or_gate = OrGate("or")
    or_gate.input0.value = False
    or_gate.input1.value = False
    print(or_gate)
    or_gate.input1.value = True
    print(or_gate)


def test_xor():
    # Testing xor
    xor_gate = XorGate("xor")
    xor_gate.input0.value = False
    xor_gate.input1.value = False
    print(xor_gate)
    xor_gate.input1.value = True
    print(xor_gate)


def test_not_not():
    not_gate1 = NotGate("not1")
    not_gate2 = NotGate("not2")
    not_gate1.output.connect(not_gate2.input)
    print(not_gate1)
    print(not_gate2)
    print("Setting not-gate input to False...")
    not_gate1.input.value = False
    print(not_gate1)
    print(not_gate2)


def test_and_not():
    and_gate = AndGate("and")
    not_gate = NotGate("not")
    and_gate.output.connect(not_gate.input)
    and_gate.input0.value = True
    and_gate.input1.value = False
    print(and_gate)
    print(not_gate)
    and_gate.input1.value = True
    print(and_gate)
    print(not_gate)


# New for Assginment #5
def full_adder(a, b, ci):
    circuit = Circuit()
    xor1 = XorGate("xor1", circuit)
    xor2 = XorGate("xor2", circuit)  # output of this is s
    and1 = AndGate("and1", circuit)
    and2 = AndGate("and2", circuit)
    or1 = OrGate("or1", circuit)  # output of this is co

    xor1.output.connect(xor2.input0)
    xor1.output.connect(and1.input1)
    and1.output.connect(or1.input0)
    and2.output.connect(or1.input1)

    xor1.input0.value = a
    xor1.input1.value = b
    xor2.input1.value = ci
    and1.input0.value = ci
    and2.input0.value = a
    and2.input1.value = b

    return xor2.output.value, or1.output.value, circuit.cost


if __name__ == '__main__':
    test_not()
