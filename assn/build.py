reg_input = ""
op_precedence_map = {"|": 1, ".": 2, "*": 3}


def is_op(symbol):
    return symbol == '.' or symbol == '|' or symbol == '*'


def add_dots_for_concatenation():
    result = ""
    for i in range(len(reg_input)):
        result += reg_input[i]
        if i < len(reg_input) - 1 and reg_input[i + 1] not in ["*", "|", ")"] and reg_input[i] not in ["(", "|"]:
            result += "."
    return result


def shunting_yard():
    result = ""
    stack = []

    for i in range(len(reg_input)):
        if reg_input[i].isdigit() or reg_input[i].islower():
            result += reg_input[i]
        elif is_op(reg_input[i]) and ((len(stack) > 0 and stack[-1] == '(') or len(stack) == 0):
            stack.append(reg_input[i])
        elif is_op(reg_input[i]) and len(stack) > 0 and op_precedence_map[stack[-1]] >= op_precedence_map[reg_input[i]]:
            while True:
                if len(stack) == 0 or stack[-1] == '(' or op_precedence_map[reg_input[i]] > op_precedence_map[
                    stack[-1]]:
                    stack.append(reg_input[i])
                    # print(stack)
                    break
                op = stack.pop()
                result += op
        elif is_op(reg_input[i]) and len(stack) > 0 and op_precedence_map[stack[-1]] < op_precedence_map[reg_input[i]]:
            stack.append(reg_input[i])
        elif reg_input[i] == ')':
            while True:
                if stack[-1] == '(':
                    stack.pop()
                    break
                op = stack.pop()
                result += op
        elif reg_input[i] == '(':
            stack.append(reg_input[i])

    while True:
        if len(stack) == 0:
            break
        op = stack.pop()
        result += op

    # print(result)
    return result


def regex_to_NFA(regex):
    nfa_stack = []
    for i in range(len(regex)):
        if regex[i].islower() or regex[i].isdigit():
            nfa = symbol_nfa(regex[i])
            nfa_stack.append(nfa)
        elif regex[i] == ".":
            nfa = concatenate_nfas(nfa_stack)
            nfa_stack.append(nfa)
        elif regex[i] == "|":
            nfa = union_nfas(nfa_stack)
            nfa_stack.append(nfa)
        elif regex[i] == "*":
            nfa = star_nfa(nfa_stack)
            nfa_stack.append(nfa)
    return nfa_stack

def symbol_nfa(symbol):
    # {0: [['a', 1] ...
    nfa = {0: [[symbol, 1]], 1: []}
    accept_states_set = {1}
    return [nfa, accept_states_set]


def concatenate_nfas(nfa_stack):
    second_nfa = nfa_stack.pop()
    first_nfa = nfa_stack.pop()
    result_nfa = {}
    result_nfa_acc_states = set()

    # copy first nfa into final nfa
    for key in sorted(get_transitions(first_nfa)):
        result_nfa[key] = first_nfa[0][key]
        if key in sorted(get_accept_states(first_nfa)):
            result_nfa_acc_states.add(key)

    for key in get_transitions(second_nfa):
        # if key is zero, we should add transitions to all accept states of first nfa
        # which transitions are coming out of start state of second_nfa
        if key == 0:
            for accept_state in sorted(get_accept_states(first_nfa)):  # {0, 1, 2, 3, 4 ...}   {0 : [[symbol, state_num] [] [] []]}
                for transition in second_nfa[0][key]:
                    if [transition[0], transition[1] + len(first_nfa[0]) - 1] not in result_nfa[accept_state]:
                        result_nfa[accept_state].append([transition[0], transition[1] + len(first_nfa[0]) - 1])
            if key in get_accept_states(second_nfa):
                # es mgoni yvela variantshi accept state iqneba da ravi iyos mainc xo
                pass
        else:
            result_nfa[len(first_nfa[0]) + key - 1] = second_nfa[0][key]
            # increment all numbers of states except number 0
            for i in range(len(result_nfa[len(first_nfa[0]) + key - 1])):  # {0: [[], [], []]}
                if result_nfa[len(first_nfa[0]) + key - 1][i][1] != 0:
                    result_nfa[len(first_nfa[0]) + key - 1][i][1] += (len(first_nfa[0]) - 1)
                else:
                    for accept_state in get_accept_states(first_nfa):
                        if [result_nfa[len(first_nfa[0]) + key - 1][i][0], accept_state] not in result_nfa[len(first_nfa[0]) + key - 1]:
                            result_nfa[len(first_nfa[0]) + key - 1].append([result_nfa[len(first_nfa[0]) + key - 1][i][0], accept_state])
            if key in get_accept_states(second_nfa):
                result_nfa_acc_states.add(len(first_nfa[0]) + key - 1)
            # pop all the elements which go to 0 index state, because each state that was going to zero
            # index state should go to first_nfa accept state
            for i in range(len(result_nfa[len(first_nfa[0]) + key - 1]) - 1, -1, -1):
                if result_nfa[len(first_nfa[0]) + key - 1][i][1] == 0:
                    result_nfa.pop(i)
            # pop first nfa accept states from result_acc_states if second_nfa accept states doesn't consist 0
            if 0 not in get_accept_states(second_nfa):
                for acc_state in result_nfa_acc_states.copy():
                    if acc_state in get_accept_states(first_nfa):
                        result_nfa_acc_states.remove(acc_state)
    return [result_nfa, result_nfa_acc_states]


def union_nfas(nfa_stack):
    second_nfa = nfa_stack.pop()
    first_nfa = nfa_stack.pop()
    result_nfa = {}
    result_nfa_acc_states = set()
    # result_nfa[0].append([])
    # result_nfa[0] = [[]]
    if (0 in get_accept_states(first_nfa)) or (0 in get_accept_states(second_nfa)):
        result_nfa_acc_states.add(0)

    # copy first nfa into final nfa
    for key in sorted(get_transitions(first_nfa)):
        result_nfa[key] = first_nfa[0][key]
        if key in sorted(get_accept_states(first_nfa)):
            result_nfa_acc_states.add(key)

    # copy second nfa into final nfa
    for key in sorted(get_transitions(second_nfa)):
        if key == 0:
            for i in range(len(second_nfa[0][key])):
                if second_nfa[0][key][i][1] != 0:
                    if [second_nfa[0][key][i][0], second_nfa[0][key][i][1] + len(first_nfa[0]) - 1] not in result_nfa[key]:
                        result_nfa[key].append([second_nfa[0][key][i][0], second_nfa[0][key][i][1] + len(first_nfa[0]) - 1])
                else:
                    if [second_nfa[0][key][i][0], second_nfa[0][key][i][1]] not in result_nfa[key]:
                        result_nfa[key].append([second_nfa[0][key][i][0], second_nfa[0][key][i][1]])
        else:
            result_nfa[len(first_nfa[0]) + key - 1] = second_nfa[0][key]
            # increment all numbers of states except number 0
            for i in range(len(result_nfa[len(first_nfa[0]) + key - 1])):
                if result_nfa[len(first_nfa[0]) + key - 1][i][1] != 0:
                    result_nfa[len(first_nfa[0]) + key - 1][i][1] += (len(first_nfa[0]) - 1)
            if key in get_accept_states(second_nfa):
                result_nfa_acc_states.add(len(first_nfa[0]) + key - 1)

    return [result_nfa, result_nfa_acc_states]


def star_nfa(nfa_stack):
    nfa = nfa_stack.pop()
    result_nfa = get_transitions(nfa)
    result_nfa_accept_states = get_accept_states(nfa)

    result_nfa_accept_states.add(0)
    for accept_state in get_accept_states(nfa):  # {7: [[], [], []]
        if accept_state == 0:
            continue
        for transition in result_nfa[0]:
            if transition not in result_nfa[accept_state]:
                result_nfa[accept_state].append(transition)

    return [result_nfa, result_nfa_accept_states]


def get_transitions(nfa):
    return nfa[0]


def get_accept_states(nfa):
    return nfa[1]


def count_transitions(transitions):
    count = 0
    for key in transitions:
        count += len(transitions[key])
    return count


def print_transitions(transitions):
    for transition in transitions:
        output = "" + str(len(transitions[transition])) + " "
        for i in range(len(transitions[transition])):
            output += str(transitions[transition][i][0]) + " " + str(transitions[transition][i][1]) + " "
        print(output)


def nfa_output(nfa):
    transitions = get_transitions(nfa)
    accept_states = get_accept_states(nfa)

    print(f"{len(transitions)} {len(accept_states)} {count_transitions(transitions)}")
    accept_states_output = ""
    for accept_state in accept_states:
        accept_states_output += str(accept_state) + " "
    print(accept_states_output)
    print_transitions(transitions)


if __name__ == "__main__":
    reg_input = input()
    reg_input = add_dots_for_concatenation()
    reg_input = shunting_yard()
    nfa_stack = regex_to_NFA(reg_input)
    nfa = nfa_stack.pop()
    nfa_output(nfa)
