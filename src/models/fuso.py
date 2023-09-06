class Fuso:
    fuso = {
        "UTM 18 S (MER -75)" : 31978, "UTM 19 N (MER -69)" : 31973, "UTM 19 S (MER -69)" : 31979, "UTM 20 N (MER -63)" : 31974, "UTM 20 S (MER -63)" : 31980,
        "UTM 21 N (MER -57)" : 31975, "UTM 21 S (MER -57)" : 31981, "UTM 22 N (MER -51)" : 31976, "UTM 22 S (MER -51)" : 31982, "UTM 23 S (MER -45)" : 31983,
        "UTM 24 S (MER -39)" : 31984, "UTM 25 S (MER -33)" : 31985
    }

    @staticmethod
    def retorna_fuso(chave):
        return Fuso.fuso[chave]
