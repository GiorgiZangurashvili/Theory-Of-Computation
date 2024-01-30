nfa = {}
accept_states_set = set()

def create_NFA():
    # NFA states
    states_input = input()

    # accept states
    accept_states_input = input()
    accept_states = accept_states_input.split()
    for i in range(len(accept_states)):
        accept_states_set.add(int(accept_states[i]))

    # transitions
    idx = 0
    for i in range(int(states_input.split()[0])):
        transition_input = input()
        transitions = transition_input.split()
        if transitions[0] == "0":
            nfa[idx] = []
            idx += 1
            continue
        else:
            for j in range(1, len(transitions), 2):
                transition_symbol = transitions[j]
                transition_state = int(transitions[j + 1])
                transition_function = (transition_symbol, transition_state)
                if idx in nfa:
                    nfa[idx].append(transition_function)
                else:
                    nfa[idx] = []
                    nfa[idx].append(transition_function)
            idx += 1

def dfs(input_string, current_state, idx, output):
    if idx == len(input_string):
        return

    if current_state in nfa:
        transition_states = nfa[current_state]
        for i in range(len(transition_states)):
            if transition_states[i][0] == input_string[idx] and transition_states[i][1] in accept_states_set:
                output[idx] = "Y"
            if transition_states[i][0] == input_string[idx]:
                dfs(input_string, transition_states[i][1], idx + 1, output)
    else:
        return


if __name__ == "__main__":
    input_string = input()
    create_NFA()
    current_state = 0
    idx = 0
    output = ["N"] * len(input_string)
    dfs(input_string, current_state, idx, output)
    output_str = ""
    for i in range(len(output)):
        output_str += output[i]
    print(output_str)
