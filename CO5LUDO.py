# ─────────────────────────────────────────────────────
# CO5 : Probability Review, Bayes Rule,
#       Bayesian Networks,
#       Variable Elimination,
#       Belief Propagation,
#       Sampling Inference,
#       Markov Chains & HMM,
#       Sensor Fusion Reasoning,
#       Uncertainty-Aware Decisions
# ─────────────────────────────────────────────────────

import random

# ─────────────────────────────────────────────────────
# PROBABILITY REVIEW
# Basic probability calculations
# ─────────────────────────────────────────────────────

def probability(success, total):

    return success / total


# Example
p = probability(1, 6)

print("Probability of rolling 6 =", p)


# ─────────────────────────────────────────────────────
# BAYES RULE
# P(A|B) = [P(B|A) * P(A)] / P(B)
# ─────────────────────────────────────────────────────

def bayes_rule(p_b_given_a, p_a, p_b):

    return (p_b_given_a * p_a) / p_b


# Example:
# Disease prediction example

p_disease = 0.01
p_positive_given_disease = 0.95
p_positive = 0.05

result = bayes_rule(
    p_positive_given_disease,
    p_disease,
    p_positive
)

print("\nBayes Rule Result =", result)


# ─────────────────────────────────────────────────────
# BAYESIAN NETWORK
# Simple dependency model
# ─────────────────────────────────────────────────────

bayesian_network = {

    "Rain": {
        True: 0.2,
        False: 0.8
    },

    "Traffic": {

        True: {
            True: 0.8,
            False: 0.2
        },

        False: {
            True: 0.3,
            False: 0.7
        }
    }
}

print("\nBayesian Network Created")


# ─────────────────────────────────────────────────────
# VARIABLE ELIMINATION
# Simplified probabilistic inference
# ─────────────────────────────────────────────────────

def variable_elimination():

    rain_probability = bayesian_network["Rain"][True]

    traffic_given_rain = bayesian_network["Traffic"][True][True]

    result = rain_probability * traffic_given_rain

    return result


print("Variable Elimination Result =",
      variable_elimination())


# ─────────────────────────────────────────────────────
# BELIEF PROPAGATION
# Updating belief after evidence
# ─────────────────────────────────────────────────────

def belief_propagation(prior, evidence):

    updated_belief = prior * evidence

    normalization = updated_belief + (1 - prior)

    return updated_belief / normalization


belief = belief_propagation(0.4, 0.9)

print("\nUpdated Belief =", belief)


# ─────────────────────────────────────────────────────
# SAMPLING INFERENCE
# Monte Carlo sampling
# ─────────────────────────────────────────────────────

def sampling_inference(samples):

    count = 0

    for _ in range(samples):

        dice = random.randint(1, 6)

        if dice == 6:
            count += 1

    return count / samples


sampling_result = sampling_inference(1000)

print("\nSampling Inference =", sampling_result)


# ─────────────────────────────────────────────────────
# MARKOV CHAIN
# State transition probabilities
# ─────────────────────────────────────────────────────

transition_matrix = {

    "Sunny": {
        "Sunny": 0.7,
        "Rainy": 0.3
    },

    "Rainy": {
        "Sunny": 0.4,
        "Rainy": 0.6
    }
}

def markov_next_state(current_state):

    rand = random.random()

    cumulative = 0

    for state, prob in transition_matrix[current_state].items():

        cumulative += prob

        if rand <= cumulative:
            return state


state = "Sunny"

print("\nMarkov Chain States")

for i in range(5):

    state = markov_next_state(state)

    print("Step", i + 1, ":", state)


# ─────────────────────────────────────────────────────
# HIDDEN MARKOV MODEL (HMM)
# Hidden states + observations
# ─────────────────────────────────────────────────────

hidden_states = ["Healthy", "Sick"]

observations = ["Normal", "Fever"]

emission_probability = {

    "Healthy": {
        "Normal": 0.8,
        "Fever": 0.2
    },

    "Sick": {
        "Normal": 0.3,
        "Fever": 0.7
    }
}

print("\nHidden Markov Model Created")


# ─────────────────────────────────────────────────────
# SENSOR FUSION REASONING
# Combine multiple uncertain sensors
# ─────────────────────────────────────────────────────

def sensor_fusion(sensor1, sensor2):

    return (sensor1 + sensor2) / 2


sensor_result = sensor_fusion(0.7, 0.9)

print("\nSensor Fusion Result =", sensor_result)


# ─────────────────────────────────────────────────────
# UNCERTAINTY-AWARE DECISIONS
# Decision making under uncertainty
# ─────────────────────────────────────────────────────

def uncertainty_decision(probability_success):

    if probability_success >= 0.7:
        return "Take Action"

    elif probability_success >= 0.4:
        return "Wait"

    else:
        return "Avoid"


decision = uncertainty_decision(0.65)

print("\nDecision =", decision)


# ─────────────────────────────────────────────────────
# COMBINED PROBABILISTIC AI EXAMPLE
# ─────────────────────────────────────────────────────

dice_probability = sampling_inference(500)

belief_score = belief_propagation(0.5, 0.8)

final_decision = uncertainty_decision(belief_score)

print("\nCombined AI Reasoning")

print("Dice Probability =", dice_probability)

print("Belief Score =", belief_score)

print("Final Decision =", final_decision)