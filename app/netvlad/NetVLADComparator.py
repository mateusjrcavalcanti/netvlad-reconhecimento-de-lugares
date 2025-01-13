import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class NetVLADComparator():
  def compare_descriptors(self, descriptor_one, descriptor_two, method='euclidean'):
      if method == 'euclidean':
          return self.euclidean_distance(descriptor_one, descriptor_two)
      elif method == 'cosine':
          return self.cosine_similarity_metric(descriptor_one, descriptor_two)
      elif method == 'manhattan':
          return self.manhattan_distance(descriptor_one, descriptor_two)
      elif method == 'chebyshev':
          return self.chebyshev_distance(descriptor_one, descriptor_two)
      elif method == 'minkowski':
          return self.minkowski_distance(descriptor_one, descriptor_two, p=3)
      elif method == 'bray_curtis':
          return self.bray_curtis_distance(descriptor_one, descriptor_two)
      else:
          raise ValueError("Método de comparação inválido. Escolha entre 'euclidean', 'cosine', 'manhattan', 'chebyshev', 'minkowski' ou 'bray_curtis'.")

  def euclidean_distance(self, descriptor_one, descriptor_two):
      return np.linalg.norm(descriptor_one - descriptor_two)

  def cosine_similarity_metric(self, descriptor_one, descriptor_two):
      return cosine_similarity(descriptor_one.reshape(1, -1), descriptor_two.reshape(1, -1))[0][0]

  def manhattan_distance(self, descriptor_one, descriptor_two):
      return np.sum(np.abs(descriptor_one - descriptor_two))

  def chebyshev_distance(self, descriptor_one, descriptor_two):
      return np.max(np.abs(descriptor_one - descriptor_two))

  def minkowski_distance(self, descriptor_one, descriptor_two, p=3):
      return np.sum(np.abs(descriptor_one - descriptor_two) ** p) ** (1 / p)

  def bray_curtis_distance(self, descriptor_one, descriptor_two):
      return np.sum(np.abs(descriptor_one - descriptor_two)) / np.sum(np.abs(descriptor_one + descriptor_two))

