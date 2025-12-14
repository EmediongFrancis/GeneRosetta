class BiophysicalEngine:
    """
    The 'Physics Engine' of GeneRosetta.
    
    This class contains the 'Universal Truths' of biology. 
    It relies on hardcoded, scientifically established constants (mass, charge, hydropathy).
    
    It is DETERMINISTIC: The same input will always produce the exact same numbers.
    It is SPECIES-AGNOSTIC: Tryptophan weighs the same in a Human as it does in a Dog.
    """
    
    # -------------------------------------------------------------------------
    # THE DATA SOURCE
    # -------------------------------------------------------------------------
    # Keys: IUPAC Single-Letter Codes (e.g., 'A' = Alanine)
    # Mass: Measured in Daltons (Da). Controls how much space the atom takes up.
    # Charge: At physiological pH (7.4). Controls magnetism (+/-).
    # Hydropathy: Kyte-Doolittle scale. 
    #   - Positive (+) numbers = Hydrophobic (Oily/Hates Water). Found inside the core.
    #   - Negative (-) numbers = Hydrophilic (Water-loving). Found on the surface.
    # -------------------------------------------------------------------------
    AMINO_ACIDS = {
        'A': {'name': 'Alanine',        'mass': 89.1,  'charge': 0,  'hydropathy': 1.8},
        'R': {'name': 'Arginine',       'mass': 174.2, 'charge': 1,  'hydropathy': -4.5},
        'N': {'name': 'Asparagine',     'mass': 132.1, 'charge': 0,  'hydropathy': -3.5},
        'D': {'name': 'Aspartic Acid',  'mass': 133.1, 'charge': -1, 'hydropathy': -3.5},
        'C': {'name': 'Cysteine',       'mass': 121.2, 'charge': 0,  'hydropathy': 2.5},
        'E': {'name': 'Glutamic Acid',  'mass': 147.1, 'charge': -1, 'hydropathy': -3.5},
        'Q': {'name': 'Glutamine',      'mass': 146.2, 'charge': 0,  'hydropathy': -3.5},
        'G': {'name': 'Glycine',        'mass': 75.1,  'charge': 0,  'hydropathy': -0.4},
        'H': {'name': 'Histidine',      'mass': 155.2, 'charge': 0.1,'hydropathy': -3.2},
        'I': {'name': 'Isoleucine',     'mass': 131.2, 'charge': 0,  'hydropathy': 4.5},
        'L': {'name': 'Leucine',        'mass': 131.2, 'charge': 0,  'hydropathy': 3.8},
        'K': {'name': 'Lysine',         'mass': 146.2, 'charge': 1,  'hydropathy': -3.9},
        'M': {'name': 'Methionine',     'mass': 149.2, 'charge': 0,  'hydropathy': 1.9},
        'F': {'name': 'Phenylalanine',  'mass': 165.2, 'charge': 0,  'hydropathy': 2.8},
        'P': {'name': 'Proline',        'mass': 115.1, 'charge': 0,  'hydropathy': -1.6},
        'S': {'name': 'Serine',         'mass': 105.1, 'charge': 0,  'hydropathy': -0.8},
        'T': {'name': 'Threonine',      'mass': 119.1, 'charge': 0,  'hydropathy': -0.7},
        'W': {'name': 'Tryptophan',     'mass': 204.2, 'charge': 0,  'hydropathy': -0.9},
        'Y': {'name': 'Tyrosine',       'mass': 181.2, 'charge': 0,  'hydropathy': -1.3},
        'V': {'name': 'Valine',         'mass': 117.2, 'charge': 0,  'hydropathy': 4.2},
    }

    @staticmethod
    def calculate_deltas(old_residue_char, new_residue_char):
        """
        Calculates the physical difference between two amino acids.
        
        Args:
            old_residue_char (str): The letter before mutation (e.g., 'W')
            new_residue_char (str): The letter after mutation (e.g., 'R')
            
        Returns:
            dict: The numerical differences, or None if invalid input.
        """
        # 1. Lookup the data for both letters
        # .get() prevents crashing if a weird letter (like 'X' or 'Z') is passed
        old_aa = BiophysicalEngine.AMINO_ACIDS.get(old_residue_char.upper())
        new_aa = BiophysicalEngine.AMINO_ACIDS.get(new_residue_char.upper())

        # If input is garbage (not a real amino acid), return None
        if not old_aa or not new_aa:
            return None

        # 2. Perform the Math (The Physics Logic)
        return {
            # MASS DELTA:
            # If Positive (+): We added weight. The new piece is bigger.
            # Implication: "Steric Hindrance" (It might not fit in the hole).
            # If Negative (-): We lost weight. The new piece is smaller.
            # Implication: "Cavity Formation" (It leaves an empty gap, destabilizing structure).
            "mass_delta": round(new_aa['mass'] - old_aa['mass'], 2),

            # CHARGE DELTA:
            # If Not Zero: We changed the magnetism.
            # e.g., +1 to -1 is a delta of -2. This is huge.
            # Implication: Breaks "Salt Bridges" (the glue holding the protein together).
            "charge_delta": new_aa['charge'] - old_aa['charge'],

            # HYDROPATHY DELTA:
            # If we go from High Positive (Oily) to High Negative (Watery).
            # Implication: The protein core might try to turn inside out to touch water.
            # This causes "Unfolding" (The protein breaks).
            "hydropathy_delta": round(new_aa['hydropathy'] - old_aa['hydropathy'], 2),

            # Metadata for the report generator
            "old_aa_name": old_aa['name'],
            "new_aa_name": new_aa['name']
        }