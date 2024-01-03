import cProfile


def profile_test():
    ''' funkcja do profilowania '''
    import main
    main.main()


if __name__ == "__main__":
    cProfile.run('profile_test()')
