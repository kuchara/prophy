from prophyc import model

def test_typedef_repr():
    typedef = model.Typedef("my_typedef", "u8")
    assert str(typedef) == "u8 my_typedef"

def test_struct_repr():
    struct = model.Struct("MyStruct", [
        model.StructMember("a", "u8"),
        model.StructMember("b", "u16", bound = 'xlen'),
        model.StructMember("c", "u32", size = 5),
        model.StructMember("d", "u64", bound = 'xlen', size = 5),
        model.StructMember("e", "UU", unlimited = True),
        model.StructMember("f", "UUUU", optional = True)
    ])
    assert str(struct) == """\
MyStruct
    u8 a
    u16 b<>(xlen)
    u32 c[5]
    u64 d<5>(xlen)
    UU e<...>
    UUUU* f
"""

def test_union_repr():
    union = model.Union("MyUnion", [
        model.UnionMember("a", "u8", 1),
        model.UnionMember("b", "u16", 2),
        model.UnionMember("c", "u32", 3)
    ])
    assert str(union.members[0]) == "1: u8 a"
    assert str(union.members[1]) == "2: u16 b"
    assert str(union.members[2]) == "3: u32 c"
    assert str(union) == """\
MyUnion
    1: u8 a
    2: u16 b
    3: u32 c
"""

def test_split_after():
    generator = model.split_after([1, 42, 2, 3, 42, 42, 5], lambda x: x == 42)
    assert [x for x in generator] == [[1, 42], [2, 3, 42], [42], [5]]

def test_model_sort_enums():
    nodes = [model.Typedef("B", "A"),
             model.Typedef("C", "A"),
             model.Enum("A", [])]

    model.topological_sort(nodes)

    assert ["A", "B", "C"] == [node.name for node in nodes]

def test_model_sort_typedefs():
    nodes = [model.Typedef("A", "X"),
             model.Typedef("C", "B"),
             model.Typedef("B", "A"),
             model.Typedef("E", "D"),
             model.Typedef("D", "C")]

    model.topological_sort(nodes)

    assert ["A", "B", "C", "D", "E"] == [node.name for node in nodes]

def test_model_sort_structs():
    nodes = [model.Struct("C", [model.StructMember("a", "B"),
                                model.StructMember("b", "A"),
                                model.StructMember("c", "D")]),
             model.Struct("B", [model.StructMember("a", "X"),
                                model.StructMember("b", "A"),
                                model.StructMember("c", "Y")]),
             model.Struct("A", [model.StructMember("a", "X"),
                                model.StructMember("b", "Y"),
                                model.StructMember("c", "Z")])]

    model.topological_sort(nodes)

    assert ["A", "B", "C"] == [node.name for node in nodes]

def test_model_sort_struct_with_two_deps():
    nodes = [model.Struct("C", [model.StructMember("a", "B")]),
             model.Struct("B", [model.StructMember("a", "A")]),
             model.Struct("A", [model.StructMember("a", "X")])]

    model.topological_sort(nodes)

    assert ["A", "B", "C"] == [node.name for node in nodes]

def test_model_sort_struct_with_multiple_dependencies():
    nodes = [model.Struct("D", [model.StructMember("a", "A"),
                                model.StructMember("b", "B"),
                                model.StructMember("c", "C")]),
             model.Struct("C", [model.StructMember("a", "A"),
                                model.StructMember("b", "B")]),
             model.Struct("B", [model.StructMember("a", "A")]),
             model.Typedef("A", "TTypeX")]

    model.topological_sort(nodes)

    assert ["A", "B", "C", "D"] == [node.name for node in nodes]

def test_model_sort_union():
    nodes = [model.Typedef("C", "B"),
             model.Union("B", [model.UnionMember("a", "A", "0"),
                               model.UnionMember("b", "A", "1")]),
             model.Struct("A", [model.StructMember("a", "X")])]

    model.topological_sort(nodes)

    assert ["A", "B", "C"] == [node.name for node in nodes]

def test_model_sort_constants():
    nodes = [model.Constant("C_C", "C_A + C_B"),
             model.Constant("C_A", "1"),
             model.Constant("C_B", "2")]

    model.topological_sort(nodes)

    assert [("C_A", "1"), ("C_B", "2"), ("C_C", "C_A + C_B")] == nodes

def test_cross_reference_structs():
    nodes = [
        model.Struct("A", [
            model.StructMember("a", "u8")
        ]),
        model.Struct("B", [
            model.StructMember("a", "A"),
            model.StructMember("b", "u8")
        ]),
        model.Struct("C", [
            model.StructMember("a", "A"),
            model.StructMember("b", "B"),
            model.StructMember("c", "NON_EXISTENT")
        ]),
        model.Struct("D", [
            model.StructMember("a", "A"),
            model.StructMember("b", "B"),
            model.StructMember("c", "C")
        ])
    ]

    model.cross_reference(nodes)

    definition_names = [[x.definition.name if x.definition else None for x in y.members] for y in nodes]
    assert definition_names == [
        [None],
        ['A', None],
        ['A', 'B', None],
        ['A', 'B', 'C']
    ]

def test_cross_reference_typedef():
    nodes = [
        model.Struct("A", [
            model.StructMember("a", "u8")
        ]),
        model.Typedef("B", "A"),
        model.Struct("C", [
            model.StructMember("a", "A"),
            model.StructMember("b", "B")
        ]),
        model.Typedef("D", "B")
    ]

    model.cross_reference(nodes)

    assert nodes[1].definition.name == "A"
    assert nodes[2].members[1].definition.definition.name == "A"
    assert nodes[3].definition.name == "B"
    assert nodes[3].definition.definition.name == "A"

def test_evaluate_kinds_arrays():
    nodes = [
        model.Struct("A", [
            model.StructMember("a", "u8"),
            model.StructMember("b", "u8", optional = True),
            model.StructMember("c", "u8", size = "5"),
            model.StructMember("d_len", "u8"),
            model.StructMember("d", "u8", bound = "d_len", size = "5"),
            model.StructMember("e_len", "u8"),
            model.StructMember("e", "u8", bound = "e_len"),
            model.StructMember("f", "u8", unlimited = True)
        ])
    ]

    model.cross_reference(nodes)
    model.evaluate_kinds(nodes)

    assert [x.kind for x in nodes[0].members] == [
        model.Kind.FIXED,
        model.Kind.FIXED,
        model.Kind.FIXED,
        model.Kind.FIXED,
        model.Kind.FIXED,
        model.Kind.FIXED,
        model.Kind.FIXED,
        model.Kind.FIXED,
    ]

def test_evaluate_kinds_struct_records():
    nodes = [
        model.Struct("Fix", [
            model.StructMember("a", "u8")
        ]),
        model.Struct("Dyn", [
            model.StructMember("a_len", "u8"),
            model.StructMember("a", "u8", bound = "a_len")
        ]),
        model.Struct("X", [
            model.StructMember("a", "Dyn"),
            model.StructMember("b_len", "u8"),
            model.StructMember("b", "Fix", bound = "b_len"),
            model.StructMember("c", "Fix", unlimited = True)
        ])
    ]

    model.cross_reference(nodes)
    model.evaluate_kinds(nodes)

    assert [x.kind for x in nodes] == [
        model.Kind.FIXED,
        model.Kind.DYNAMIC,
        model.Kind.UNLIMITED,
    ]

    assert [x.kind for x in nodes[2].members] == [
        model.Kind.DYNAMIC,
        model.Kind.FIXED,
        model.Kind.FIXED,
        model.Kind.FIXED,
    ]

def test_evaluate_kinds_with_typedefs():
    nodes = [
        model.Struct("Empty", []),
        model.Struct("Dynamic", [
            model.StructMember("a_len", "u8"),
            model.StructMember("a", "u8", bound = "a_len")
        ]),
        model.Struct("Fixed", [
            model.StructMember("a", "u8", size = "10")
        ]),
        model.Struct("Limited", [
            model.StructMember("a_len", "u8"),
            model.StructMember("a", "u8", bound = "a_len", size = "10")
        ]),
        model.Struct("Greedy", [
            model.StructMember("a", "byte", unlimited = True)
        ]),
        model.Struct("DynamicWrapper", [
            model.StructMember("a", "Dynamic")
        ]),
        model.Struct("GreedyWrapper", [
            model.StructMember("a", "Greedy")
        ]),
        model.Struct("GreedyDynamic", [
            model.StructMember("a", "Dynamic", unlimited = True)
        ]),
        model.Typedef("TU8", "u8"),
        model.Typedef("TDynamic", "Dynamic"),
        model.Typedef("TGreedy", "Greedy"),
        model.Struct("TypedefedU8", [
            model.StructMember("a", "TU8")
        ]),
        model.Struct("TypedefedDynamic", [
            model.StructMember("a", "TDynamic")
        ]),
        model.Struct("TypedefedGreedy", [
            model.StructMember("a", "TGreedy")
        ]),
        model.Typedef("TTDynamic", "TDynamic"),
        model.Typedef("TTTDynamic", "TTDynamic"),
        model.Struct("DeeplyTypedefed", [
            model.StructMember("a", "TTTDynamic")
        ]),
    ]

    model.cross_reference(nodes)
    model.evaluate_kinds(nodes)

    assert [x.kind for x in nodes if isinstance(x, model.Struct)] == [
        model.Kind.FIXED,
        model.Kind.DYNAMIC,
        model.Kind.FIXED,
        model.Kind.FIXED,
        model.Kind.UNLIMITED,
        model.Kind.DYNAMIC,
        model.Kind.UNLIMITED,
        model.Kind.UNLIMITED,
        model.Kind.FIXED,
        model.Kind.DYNAMIC,
        model.Kind.UNLIMITED,
        model.Kind.DYNAMIC,
    ]

def test_partition_fixed():
    nodes = [
        model.Struct("Fixed", [
            model.StructMember("a", "u8"),
            model.StructMember("b", "u8"),
            model.StructMember("c", "u8")
        ])
    ]

    model.cross_reference(nodes)
    model.evaluate_kinds(nodes)
    main, parts = model.partition(nodes[0].members)

    assert [x.name for x in main] == ["a", "b", "c"]
    assert [[x.name for x in part] for part in parts] == []

def test_partition_many_arrays():
    nodes = [
        model.Struct("ManyArrays", [
            model.StructMember("num_of_a", "u8"),
            model.StructMember("a", "u8", bound = "num_of_a"),
            model.StructMember("num_of_b", "u8"),
            model.StructMember("b", "u8", bound = "num_of_b"),
            model.StructMember("num_of_c", "u8"),
            model.StructMember("c", "u8", bound = "num_of_c")
        ]),
    ]

    model.cross_reference(nodes)
    model.evaluate_kinds(nodes)
    main, parts = model.partition(nodes[0].members)

    assert [x.name for x in main] == ["num_of_a", "a"]
    assert [[x.name for x in part] for part in parts] == [["num_of_b", "b"], ["num_of_c", "c"]]

def test_partition_many_arrays_mixed():
    nodes = [
        model.Struct("ManyArraysMixed", [
            model.StructMember("num_of_a", "u8"),
            model.StructMember("num_of_b", "u8"),
            model.StructMember("a", "u8", bound = "num_of_a"),
            model.StructMember("b", "u8", bound = "num_of_b")
        ]),
    ]

    model.cross_reference(nodes)
    model.evaluate_kinds(nodes)
    main, parts = model.partition(nodes[0].members)

    assert [x.name for x in main] == ["num_of_a", "num_of_b", "a"]
    assert [[x.name for x in part] for part in parts] == [["b"]]

def test_partition_dynamic_struct():
    nodes = [
        model.Struct("Dynamic", [
            model.StructMember("num_of_a", "u8"),
            model.StructMember("a", "u8", bound = "num_of_a")
        ]),
        model.Struct("X", [
            model.StructMember("a", "u8"),
            model.StructMember("b", "Dynamic"),
            model.StructMember("c", "u8")
        ])
    ]

    model.cross_reference(nodes)
    model.evaluate_kinds(nodes)
    main, parts = model.partition(nodes[1].members)

    assert [x.name for x in main] == ["a", "b"]
    assert [[x.name for x in part] for part in parts] == [["c"]]

def test_partition_many_dynamic_structs():
    nodes = [
        model.Struct("Dynamic", [
            model.StructMember("num_of_a", "u8"),
            model.StructMember("a", "u8", bound = "num_of_a")
        ]),
        model.Struct("X", [
            model.StructMember("a", "Dynamic"),
            model.StructMember("b", "Dynamic"),
            model.StructMember("c", "Dynamic")
        ])
    ]

    model.cross_reference(nodes)
    model.evaluate_kinds(nodes)
    main, parts = model.partition(nodes[1].members)

    assert [x.name for x in main] == ["a"]
    assert [[x.name for x in part] for part in parts] == [["b"], ["c"]]

def process(nodes):
    model.cross_reference(nodes)
    model.evaluate_kinds(nodes)
    model.evaluate_sizes(nodes)
    return nodes

def get_size_and_alignment(node):
    return (node.byte_size, node.alignment)

def get_members_and_node(node):
    return node.members + [node]

def test_evaluate_sizes_struct():
    nodes = process([
        model.Struct('X', [
            model.StructMember('x', 'u16'),
            model.StructMember('y', 'u8')
        ])
    ])
    assert map(get_size_and_alignment, get_members_and_node(nodes[0])) == [
        (2, 2),
        (1, 1),
        (4, 2)
    ]

def test_evaluate_sizes_fixed_array():
    nodes = process([
        model.Struct('X', [
            model.StructMember('x', 'u32'),
            model.StructMember('y', 'u8', size = '3')
        ])
    ])
    assert map(get_size_and_alignment, get_members_and_node(nodes[0])) == [
        (4, 4),
        (3, 1),
        (8, 4)
    ]

def test_evaluate_sizes_dynamic_array():
    nodes = process([
        model.Struct('X', [
            model.StructMember('num_of_x', 'u32'),
            model.StructMember('x', 'u8', bound = 'num_of_x'),
        ])
    ])
    assert map(get_size_and_alignment, get_members_and_node(nodes[0])) == [
        (4, 4),
        (0, 1),
        (4, 4)
    ]

def test_evaluate_sizes_limited_array():
    nodes = process([
        model.Struct('X', [
            model.StructMember('num_of_x', 'u32'),
            model.StructMember('x', 'u8', bound = 'num_of_x', size = '2'),
        ])
    ])
    assert map(get_size_and_alignment, get_members_and_node(nodes[0])) == [
        (4, 4),
        (2, 1),
        (8, 4)
    ]

def test_evaluate_sizes_greedy_array():
    nodes = process([
        model.Struct('X', [
            model.StructMember('num_of_x', 'u32'),
            model.StructMember('x', 'u8', unlimited = True),
        ])
    ])
    assert map(get_size_and_alignment, get_members_and_node(nodes[0])) == [
        (4, 4),
        (0, 1),
        (4, 4)
    ]

def test_evaluate_sizes_nested_struct():
    nodes = process([
        model.Struct('U16', [
            model.StructMember('x', 'u16'),
        ]),
        model.Struct('X', [
            model.StructMember('x', 'u8'),
            model.StructMember('y', 'U16'),
        ])
    ])
    assert map(get_size_and_alignment, get_members_and_node(nodes[1])) == [
        (1, 1),
        (2, 2),
        (4, 2)
    ]

def test_evaluate_sizes_partial_padding():
    nodes = process([
        model.Struct('D', [
            model.StructMember('num_of_x', 'u32'),
            model.StructMember('x', 'u32', bound = 'num_of_x')
        ]),
        model.Struct('X', [
            model.StructMember('num_of_x', 'u32'),
            model.StructMember('x', 'u8', bound = 'num_of_x'),
            model.StructMember('y', 'u8'),
            model.StructMember('z', 'u64'),
        ]),
        model.Struct('Y', [
            model.StructMember('num_of_x', 'u32'),
            model.StructMember('x', 'u8', bound = 'num_of_x'),
            model.StructMember('num_of_y', 'u32'),
            model.StructMember('y', 'u64', bound = 'num_of_y'),
        ]),
        model.Struct('Z', [
            model.StructMember('d1', 'D'),
            model.StructMember('x', 'u8'),
            model.StructMember('d2', 'D'),
            model.StructMember('y1', 'u8'),
            model.StructMember('y2', 'u64'),
            model.StructMember('d3', 'D'),
            model.StructMember('z1', 'u8'),
            model.StructMember('z2', 'u8'),
            model.StructMember('z3', 'u16'),
        ])
    ])
    assert map(get_size_and_alignment, get_members_and_node(nodes[1])) == [
        (4, 4),
        (0, 1),
        (1, 8),
        (8, 8),
        (24, 8)
    ]
    assert map(get_size_and_alignment, get_members_and_node(nodes[2])) == [
        (4, 4),
        (0, 1),
        (4, 8),
        (0, 8),
        (16, 8)
    ]
    assert map(get_size_and_alignment, get_members_and_node(nodes[3])) == [
        (4, 4),
        (1, 4),
        (4, 4),
        (1, 8),
        (8, 8),
        (4, 4),
        (1, 2),
        (1, 1),
        (2, 2),
        (40, 8)
    ]
