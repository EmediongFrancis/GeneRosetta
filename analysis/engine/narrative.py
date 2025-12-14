class NarrativeComposer:
    """
    Determinist Logic Engine for Natural Language Generation.
    Fills templates based on data values.
    """
    
    @staticmethod
    def generate_report(context):
        """
        context dictionary must contain:
        - biophysics (mass_delta, charge_delta, etc)
        - clinical (significance, disease) OR functional (function)
        - organism
        """
        report_parts = []
        
        # 1. THE HEADLINE (Context dependent)
        bio = context.get('biophysics') or {}
        clin = context.get('clinical') or {}
        func = context.get('functional') or {}
        
        if clin.get('significance'):
            report_parts.append(f"**Clinical Impact:** This variant is classified as {clin['significance']}.")
            if clin.get('disease') and 'unspecified' not in clin['disease'].lower():
                report_parts.append(f"It is associated with {clin['disease']}.")
        elif func.get('function'):
             # Limit function text to first sentence to keep it readable
            func_summary = func['function'].split('.')[0] + "."
            report_parts.append(f"**Biological Function:** {func_summary}")
        
        # 2. THE BIOPHYSICS (The "Why")
        old_aa = bio.get('old_aa_name', 'Unknown')
        new_aa = bio.get('new_aa_name', 'Unknown')
        report_parts.append(f"\n**Molecular Mechanism:** At this position, {old_aa} is replaced by {new_aa}.")

        # Mass Logic
        mass_delta = bio.get('mass_delta', 0)
        if mass_delta > 30:
            report_parts.append("This introduces a significantly larger residue, likely causing steric hindrance (overcrowding) in the protein core.")
        elif mass_delta < -30:
            report_parts.append("This replaces a large residue with a much smaller one, potentially creating an empty cavity that destabilizes the structure.")
            
        # Charge Logic
        charge_delta = bio.get('charge_delta', 0)
        if abs(charge_delta) != 0:
            report_parts.append("This mutation alters the local electrostatic charge, which can disrupt critical salt-bridge interactions or binding sites.")

        # Hydropathy Logic
        hydro_delta = bio.get('hydropathy_delta', 0)
        if hydro_delta > 2.0:
            report_parts.append("A hydrophilic residue is replaced by a hydrophobic one, potentially causing aggregation.")
        elif hydro_delta < -2.0:
            report_parts.append("A hydrophobic core residue is replaced by a water-loving one, which is a strong driver of protein unfolding.")

        return " ".join(report_parts)