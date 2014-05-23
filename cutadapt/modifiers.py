import re
from cutadapt.qualtrim import quality_trim_index
from cutadapt.compat import PY3, maketrans


class LengthTagModifier(object):
	"""
	Replace "length=..." strings in read names.
	"""
	def __init__(self, length_tag):
		self.regex = re.compile(r"\b" + length_tag + r"[0-9]*\b")
		self.length_tag = length_tag

	def __call__(self, read):
		read = read[:]
		if read.name.find(self.length_tag) >= 0:
			read.name = self.regex.sub(self.length_tag + str(len(read.sequence)), read.name)
		return read


class SuffixRemover(object):
	"""
	Remove a given suffix from read names.
	"""
	def __init__(self, suffix):
		self.suffix = suffix

	def __call__(self, read):
		read = read[:]
		if read.name.endswith(self.suffix):
			read.name = read.name[:-len(self.suffix)]
		return read


class PrefixSuffixAdder(object):
	"""
	Add a suffix and a prefix to read names
	"""
	def __init__(self, prefix, suffix):
		self.prefix = prefix
		self.suffix = suffix

	def __call__(self, read):
		read = read[:]
		read.name = self.prefix + read.name + self.suffix
		return read


class DoubleEncoder(object):
	"""
	Double-encode colorspace reads, using characters ACGTN to represent colors.
	"""
	def __init__(self):
		self.double_encode_trans = maketrans(b'0123.', b'ACGTN')

	def __call__(self, read):
		read = read[:]
		read.sequence = read.sequence.translate(self.double_encode_trans)
		return read


class ZeroCapper(object):
	"""
	Change negative quality values of a read to zero
	"""
	def __init__(self, quality_base=33):
		qb = quality_base
		if PY3:
			self.zero_cap_trans = maketrans(bytes(range(qb)), bytes([qb] * qb))
		else:
			self.zero_cap_trans = maketrans(''.join(map(chr, range(qb))), chr(qb) * qb)

	def __call__(self, read):
		read = read[:]
		read.qualities = read.qualities.translate(self.zero_cap_trans)
		return read


def PrimerTrimmer(read):
	"""Trim primer base from colorspace reads"""
	read = read[1:]
	read.primer = b''
	return read


class QualityTrimmer(object):
	def __init__(self, cutoff, base):
		self.cutoff = cutoff
		self.base = base
		self.trimmed_bases = 0

	def __call__(self, read):
		index = quality_trim_index(read.qualities, self.cutoff, self.base)
		self.trimmed_bases += len(read.qualities) - index
		return read[:index]
