import sys
from pathlib import Path

sys.path.insert(0, 'scripts/enhanced')

from estimation_spec_parser import parse_specification

try:
    spec = parse_specification(Path('scripts/enhanced/estimation_spec_AC2013.yaml'))
    print('SUCCESS!')
    print(f'Params: {len(spec.all_param_names)}')
    print(f'Has 4-group: {spec.has_couples_gender_specific_params()}')
    print(f'\nFirst 20 params:')
    for i, p in enumerate(spec.all_param_names[:20], 1):
        print(f'  {i:2d}. {p}')

    print(f'\nLast 10 params:')
    for i, p in enumerate(spec.all_param_names[-10:], len(spec.all_param_names)-9):
        print(f'  {i:2d}. {p}')

    # Check for gender-specific parameters
    sm_params = [p for p in spec.all_param_names if p.endswith('_sm')]
    sf_params = [p for p in spec.all_param_names if p.endswith('_sf')]
    m_params = [p for p in spec.all_param_names if p.endswith('_m') and not p.endswith('_sm')]
    f_params = [p for p in spec.all_param_names if p.endswith('_f') and not p.endswith('_sf')]

    print(f'\nGender-specific parameter counts:')
    print(f'  Singles male (_sm): {len(sm_params)}')
    print(f'  Singles female (_sf): {len(sf_params)}')
    print(f'  Couples male (_m): {len(m_params)}')
    print(f'  Couples female (_f): {len(f_params)}')

except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
