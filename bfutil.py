from loci.formats import ImageReader


class BioformatsUtil:

    @staticmethod
    def isImage(path):
        baseReader = ImageReader()
        readers = baseReader.getReaders()
        rtype = None
        for reader in readers:
            if reader.isThisType(path):
                rtype = reader        
        return not rtype is None