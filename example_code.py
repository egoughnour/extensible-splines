from extensible_splines.splines import SplineEditor, BSpline

def main():
    editor = SplineEditor(BSpline())
    editor.init_figure(caption='G2, C2 Continuous Splines')

if __name__ == '__main__':
    main()