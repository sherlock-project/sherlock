"""
Kullanici Adi Varyasyon Uretici
Farkli varyasyonlar olusturur
"""

from typing import List, Set
import itertools


class UsernameGenerator:
    """Kullanici adi varyasyon uretici"""

    # Sembol degisimleri
    SEPARATORS = ['.', '_', '-', '']

    # Sona/one eklenecekler
    PREFIXES = ['the', 'real', 'official', 'mr', 'ms', 'iam', 'its']
    SUFFIXES = ['official', 'real', 'hq', 'tv', 'blog', 'news']

    # Sayi ekleri
    COMMON_NUMBERS = ['1', '2', '3', '01', '02', '03', '123', '2024', '2025']
    YEAR_RANGE = range(1990, 2026, 1)

    # Karakter degisimleri (leetspeak)
    CHAR_REPLACEMENTS = {
        'a': ['@', '4'],
        'e': ['3'],
        'i': ['1', '!'],
        'o': ['0'],
        's': ['$', '5'],
        't': ['7'],
    }

    def __init__(self, base_username: str):
        self.base = base_username.lower().strip()
        self.variations: Set[str] = set()

    def generate_all(self, max_results: int = 50) -> List[str]:
        """
        Tum varyasyonlari uret

        Args:
            max_results: Maksimum sonuc sayisi

        Returns:
            Varyasyon listesi
        """
        self.variations = {self.base}

        # Temel varyasyonlar
        self._add_separator_variations()
        self._add_number_suffixes()
        self._add_prefix_suffix()
        self._add_leetspeak_variations()

        # Sirala ve sinirla
        result = sorted(self.variations)
        return result[:max_results]

    def _add_separator_variations(self):
        """Sembol degisim varyasyonlari"""
        if ' ' in self.base:
            parts = self.base.split()
            for sep in self.SEPARATORS:
                self.variations.add(sep.join(parts))

    def _add_number_suffixes(self):
        """Sayi ekli varyasyonlar"""
        for num in self.COMMON_NUMBERS:
            self.variations.add(f'{self.base}{num}')

        for year in self.YEAR_RANGE:
            self.variations.add(f'{self.base}{year}')

    def _add_prefix_suffix(self):
        """One/sona ekli varyasyonlar"""
        for prefix in self.PREFIXES:
            self.variations.add(f'{prefix}{self.base}')
            for sep in ['', '_', '.']:
                self.variations.add(f'{prefix}{sep}{self.base}')

        for suffix in self.SUFFIXES:
            self.variations.add(f'{self.base}{suffix}')
            for sep in ['', '_', '.']:
                self.variations.add(f'{self.base}{sep}{suffix}')

    def _add_leetspeak_variations(self):
        """Leetspeak varyasyonlari"""
        variations = [self.base]

        for char, replacements in self.CHAR_REPLACEMENTS.items():
            new_variations = []
            for var in variations:
                if char in var:
                    for replacement in replacements:
                        new_var = var.replace(char, replacement)
                        new_variations.append(new_var)
            variations.extend(new_variations)

        self.variations.update(variations)

    def get_similar_patterns(self) -> List[str]:
        """Benzer kalip varyasyonlari"""
        patterns = []

        # Tekrarli karakterler
        if len(self.base) > 2:
            for i in range(len(self.base)):
                if i < len(self.base) - 1 and self.base[i] == self.base[i+1]:
                    patterns.append(self.base[:i] + self.base[i+1:])

        # Cift karakter
        for i in range(len(self.base) - 1):
            doubled = self.base[:i+1] + self.base[i] + self.base[i+1:]
            patterns.append(doubled)

        return list(set(patterns))[:10]
