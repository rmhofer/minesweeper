import json

import numpy as np

import mdp as m

with open("stimuli/stimuli_5_5_6.json") as f:
    stimuli = json.load(f)


results = []

for i, stim in enumerate(stimuli):
    print(i)
    results.append({"idx": i, "stim_params": stim})
    states = None
    for goal in ["naive_easy_probe", "naive_hard_probe", "non_naive_probe"]:
        print(goal)
        state = np.array(stim["game_state"])
        mdp = m.MineSweeper(
            state, *stim[goal], n_mines=stim["num_mines"]
        )
        if goal == "naive_easy_probe":
            states = mdp.traverse(mdp.board_to_state(state))
        Q, V = m.vi(mdp, states)

        results[-1]["Q_" + goal] = {k: v.tolist() for k, v in Q.items()}
    print("-" * 20)

with open("stimuli/model_results.json", "w") as f:
    json.dump(results, f)