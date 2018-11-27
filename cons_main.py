from info_getter import InfoGetter


class Main():
    @staticmethod
    def main():
        getter = InfoGetter()
        print(getter.get_info_table())


if __name__ == '__main__':
    Main.main()
