import numpy as np

def find_nth(haystack, needle, n):
    """ Find the nth occurrence of sub-string in string.
     """
    try:
        start = haystack.find(needle)
        while start >= 0 and n > 1:
            start = haystack.find(needle, start + len(needle))
            n -= 1
    except AttributeError:
        print("check")

    return start


def softmax_with_temperature(logits, temperature):
    logits = np.array(logits)
    # Apply temperature scaling
    logits = logits/temperature

    # Compute softmax
    exp_logits = np.exp(logits)
    softmax_probs = exp_logits / np.sum(exp_logits)

    return softmax_probs