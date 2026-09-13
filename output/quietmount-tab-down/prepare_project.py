from pathlib import Path
s=(Path(__file__).resolve().parent.parent/'quietmount-mixed-screws/prepare_project.py').read_text()
s=s.replace('QuietMount_Mixed_Screws','QuietMount_Tab_Down')
s=s.replace('20 bodies - 9 tapered and 11 mushroom','Tab down - rounded tabs - 9 tapered 11 mushroom')
exec(compile(s,__file__,'exec'))
