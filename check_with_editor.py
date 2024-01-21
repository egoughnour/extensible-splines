import splines
import interactive

def main():
    editor = interactive.SplineEditor(splines.BSpline())
    editor.init_figure(caption='G2, C2 Continuous Splines')


if __name__ == '__main__':
    main()