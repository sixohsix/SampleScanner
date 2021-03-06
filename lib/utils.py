import itertools
import numpy
import math
from numpy import inf

from constants import default_silence_threshold, bit_depth
from collections import defaultdict


NOTE_NAMES = [
    'A', 'Bb', 'B', 'C', 'Db', 'D',
    'Eb', 'E', 'F', 'Gb', 'G', 'Ab'
]


def note_name(note):
    from_c = int(int(note) - 21)
    note_name = NOTE_NAMES[(from_c % 12)]
    octave_number = (from_c / 12)
    return "%s%d" % (note_name, octave_number)


def note_number(note_name):
    octave_number = int(note_name[-1])
    note = note_name[:-1]
    return 21 + NOTE_NAMES.index(note) + (12 * octave_number)


def warn_on_clipping(data, threshold=0.9999):
    if numpy.amax(numpy.absolute(data)) > ((2 ** (bit_depth - 1)) * threshold):
        print "WARNING: Clipping detected!"


def sample_value_to_db(value, bit_depth=bit_depth):
    if value == 0:
        return -inf
    return 20. * math.log(float(abs(value)) / (2 ** (bit_depth - 1)), 10)


def percent_to_db(percent):
    if percent == 0:
        return -inf
    return 20. * math.log(percent, 10)


def trim_data(
    data,
    start_threshold=default_silence_threshold,
    end_threshold=default_silence_threshold
):
    start, end = min([start_of(chan, start_threshold) for chan in data]), \
        max([end_of(chan, end_threshold) for chan in data])

    return data[0:, start:end]


def trim_mono_data(
    data,
    start_threshold=default_silence_threshold,
    end_threshold=default_silence_threshold
):
    start, end = start_of(data, start_threshold), end_of(data, end_threshold)
    return data[start:end]


def normalized(list):
    return list.astype(numpy.float32) / float(numpy.amax(numpy.abs(list)))


def start_of(list, threshold=default_silence_threshold, samples_before=1):
    if int(threshold) != threshold:
        threshold = threshold * float(2 ** (bit_depth - 1))
    index = numpy.argmax(numpy.absolute(list) > threshold)
    if index > (samples_before - 1):
        return index - samples_before
    else:
        return 0


def end_of(list, threshold=default_silence_threshold, samples_after=1):
    if int(threshold) != threshold:
        threshold = threshold * float(2 ** (bit_depth - 1))
    rev_index = numpy.argmax(
        numpy.flipud(numpy.absolute(list)) > threshold
    )
    if rev_index > (samples_after - 1):
        return len(list) - (rev_index - samples_after)
    else:
        return len(list)


def first_non_none(list):
    try:
        return next(item for item in list if item is not None)
    except StopIteration:
        return None


def group_by_attr(data, attrs):
    if not isinstance(attrs, list):
        attrs = [attrs]
    groups = defaultdict(list)
    for k, g in itertools.groupby(
        data,
        lambda x: first_non_none([
            x.attributes.get(attr, None) for attr in attrs
        ])
    ):
        groups[k].extend(list(g))
    return groups
