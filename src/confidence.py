"""Qualitative judgments only; no scoring, weighting or legal probabilities."""
STATES = {
    'Confirmed', 'Strongly supported', 'Probable / analytic judgment',
    'Alleged / unverified', 'Unresolved', 'Rejected',
}
CONFIDENCE = {'High', 'Moderate', 'Low', 'Unknown'}
MATURITY = {'Established', 'Corroborated', 'Analytic', 'Experimental', 'Open dependency'}


def is_open(claim):
    return claim['status'] == 'Unresolved' or claim['maturity'] == 'Open dependency'
