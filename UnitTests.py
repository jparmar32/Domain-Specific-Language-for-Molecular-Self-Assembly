'''
Created on Apr 16, 2018

@author: Jupinder Parmar
'''
'''
Created on Aug 10, 2016

@author: jupiparmar1
'''
import unittest
import tam3
from tam3 import MultisignalType, Multisignal, Neighborhood,\
    SignalInvalidValueError, NonexistentTransitionError,\
    InvalidChooserTileTemplateError, NameDifferenceError,\
    NonexistentChooserSetError, ChooserSet
from tam3 import TileTemplate





class Test(unittest.TestCase):


    def setUp(self):

         self.tile = tam3.Tile(name='exTile', label='tile', textcolor='black', westglue=('west', 2),northglue=('north', 2))


    ## Non tile functions
    def test_identity(self):
         exTuple = (1,'a',3)
         self.assertEqual(tam3.identity(exTuple), (1,'a',3))
    def test_oppositeDirection(self):
         W = tam3.Direction.West
         nonDet = tam3.Direction.Nondet
         self.assertEquals(tam3.oppositeDirection(W), tam3.Direction.East)
         self.assertRaises(ValueError, lambda: tam3.oppositeDirection(nonDet))
    ## Tile Methods

    def test_reflectNS(self):
        orig_tile = tam3.Tile(name='tile', northglue=('N',2), southglue=('S',1), westglue=('W',1), eastglue=('E',1))
        reflected_tile_expected = tam3.Tile(name='tile', northglue=('S',1), southglue=('N',2), westglue=('W',1), eastglue=('E',1))
        reflected_tile_actual = orig_tile.reflectNS()
        self.assertEquals(reflected_tile_actual, reflected_tile_expected)
#

    def test_reflectEW(self):
        orig_tile = tam3.Tile(name='tile', northglue=('N',1), southglue=('S',1), westglue=('W',2), eastglue=('E',1))
        reflected_tile_expected = tam3.Tile(name='tile', northglue=('N',1), southglue=('S',1), westglue=('E',1), eastglue=('W',2))
        reflected_tile_actual = orig_tile.reflectEW()
        self.assertEquals(reflected_tile_actual, reflected_tile_expected)
    def test_rotateLeft(self):
        orig_tile = tam3.Tile(name='tile', northglue=('N',2), southglue=('S',1), westglue=('W',1), eastglue=('E',1))
        reflected_tile_expected = tam3.Tile(name='tile', northglue=('E',1), southglue=('W',1), westglue=('N',2), eastglue=('S',1))
        reflected_tile_actual = orig_tile.rotateLeft()
        self.assertEquals(reflected_tile_actual, reflected_tile_expected)
    def test_rotateRight(self):
        orig_tile = tam3.Tile(name='tile', northglue=('N',2), southglue=('S',1), westglue=('W',1), eastglue=('E',1))
        reflected_tile_expected = tam3.Tile(name='tile', northglue=('W',1), southglue=('E',1), westglue=('S',1), eastglue=('N',2))
        reflected_tile_actual = orig_tile.rotateRight()
        self.assertEquals(reflected_tile_actual, reflected_tile_expected)
    def test_rotate180(self):
        orig_tile = tam3.Tile(name='tile', northglue=('N',2), southglue=('S',1), westglue=('W',1), eastglue=('E',1))
        reflected_tile_expected = tam3.Tile(name='tile', northglue=('S',1), southglue=('N',2), westglue=('E',1), eastglue=('W',1))
        reflected_tile_actual = orig_tile.rotate180()
        self.assertEquals(reflected_tile_actual, reflected_tile_expected)
     ## TileSystem Methods
    def test_addTileTypes(self):
        tileOne = tam3.Tile(name='tile', northglue=('N',2), southglue=('S',1), westglue=('W',1), eastglue=('E',1))
        firstTemp = tam3.TileTemplate(name="first")
        tst = tam3.TileSetTemplate()
        tst.join(1, tam3.Direction.East, tileOne, firstTemp, eastglue = 'E')

        tiles = tst.createTiles()
        tileSystem = tam3.TileSystem("exTest",tiles)
        tileTwo = tam3.Tile(name='tile', northglue=('E',1), southglue=('W',1), westglue=('N',2), eastglue=('S',1))

        tileSystem.addTileTypes([tileTwo])
        self.assertEqual(tileSystem.tileTypes, [tam3.Tile(concentration=1, eastglue=('', 0), label='', name='first_West:eastglue=E', northglue=('', 0), southglue=('', 0), textcolor='black', tilecolor='white', westglue=('eastglue=E;tile-E>first', 1)), tam3.Tile(concentration=1, eastglue=('S', 1), label='', name='tile', northglue=('E', 1), southglue=('W', 1), textcolor='black', tilecolor='white', westglue=('N', 2))])
    ## MultisiginalType Methods
    def test_noChoiceMultisignal(self):
        mst = tam3.MultisignalType(s1 = [1,2,3,4], s2=[8], s3=[6,7], s4=[2])
        mst_restricted = tam3.MultisignalType(s2=[8], s4=[2])
        ##ms = tam3.Multisignal([('s2',8), ('s4',2)])
        ms = list(mst_restricted.multisignals())[0]
        self.assertEquals(mst.noChoiceMultisignal(), ms)

    def test_addSignalTypes(self):
        mst = tam3.MultisignalType(signal = (0,1))
        with self.assertRaises(tam3.SignalDuplicateNameError):
             mst.addSignalTypes(signal = (0,1))

    def test_removeSignalTypes(self):
        mst = tam3.MultisignalType(s1 = [4,6,3], s2 = [2])
        with self.assertRaises(tam3.SignalInvalidNameError):
             mst.removeSignalTypes('test')
    def test_create(self):
        mst = tam3.MultisignalType(s2 = [2])
        msc = mst.create(**{"s2" : 2})
        ms = list(mst.multisignals())[0]
        self.assertEqual(msc, ms)
        with self.assertRaises(tam3.SignalInvalidNameError):
            msnn = mst.create(**{"test" : 2})
        with self.assertRaises(tam3.SignalInvalidValueError):
            msnn = mst.create(**{"s2" : 1})

    def test_createNoNameCheck(self):
         mst = tam3.MultisignalType(signal = (0))
         msnc = mst.createNoNameCheck(**{"signal" : 0})
         ms = list(mst.multisignals())[0]
         self.assertEqual(msnc, ms)
         with self.assertRaises(tam3.SignalInvalidValueError):
            msnn = mst.createNoNameCheck(**{"signal" : 1})

    def test_restrict(self):
         mst = tam3.MultisignalType(signal = (0))
         msnc = mst.restrict(**{"signal" : 0})
         self.assertEquals(msnc["signal"], (0,))

         with self.assertRaises(tam3.SignalInvalidNameError):
            msnn = mst.restrict(**{"test" : 0})
         with self.assertRaises(tam3.SignalInvalidValueError):
            msnn = mst.restrict(**{"signal" : 1})

    def test_multisignals(self):
        mst = tam3.MultisignalType(s1 = [4,6,3])
        ms = list(mst.multisignals())[0]
        self.assertEquals(str(ms), "s1=4")
    def test_nameUnion(self):
        carryMst = tam3.MultisignalType(carry=[1,2])
        borrowMst = tam3.MultisignalType(borrow=[2,3])
        carryBorrowMst = carryMst.nameUnion(borrowMst)
        mstl = (list(carryBorrowMst)[0])
        mst = tam3.MultisignalType(borrow = [2,3], carry = [1,2] )
        ms = list(mst.multisignals())[0]
        self.assertEqual(mstl, ms)
    def test_valueUnion(self):
        carryMst = tam3.MultisignalType(carry=[1,2])
        borrowMst = tam3.MultisignalType(carry=[2,3])
        carryBorrowMst = carryMst.valueUnion(borrowMst)
        valms = (list(carryBorrowMst))
        mst = tam3.MultisignalType(carry = [1,2,3] )
        ms = list(mst.multisignals())
        self.assertEqual(valms, ms)

    def test_isValidMultisignal(self):
        mst = tam3.MultisignalType(s1 = (2))
        ms = tam3.Multisignal({"s1" : 2})
        msn = mst.isValidMultisignal(ms)
        self.assertEqual(msn, True)
    ##Multisignal Unit Tests
    def test_NameUnionDuplicateSignalsAllowed(self):
       ms = tam3.Multisignal([("s1", 1)])
       ms2 = tam3.Multisignal([("s1", 1)])
       nameUnion = ms.nameUnionDuplicateSignalAllowed(ms2)
    ##GlueTemplate Unit TEsts
    def test_createGlue(self):

        mst = tam3.MultisignalType(test = [1])
        ms = mst.create(**{"test" : 1})
        mss = list(mst.multisignals())[0]
        gt = tam3.GlueTemplate(strength=1,multisignalType=mst)
        gtc = gt.create(**{"test" : 1})

        self.assertEqual(gtc,('test=1',1))

    def test_createLabel(self):
        mst = tam3.MultisignalType(test = [1])
        mss = list(mst.multisignals())[0]
        gt = tam3.GlueTemplate(strength=1,multisignalType=mst)
        gtc = gt.createLabel(**{"test" : 1})
        self.assertEqual(gtc,str(mss))
    def test_glues(self):
        mst = tam3.MultisignalType(test = [1])
        mss = list(mst.multisignals())[0]
        gt = tam3.GlueTemplate(strength=1,multisignalType=mst)
        gtc = list(gt.glues())[0]
        self.assertEqual(gtc,('test=1',1))
    ##Transition Unit Tests
    def test_apply(self):
        trans = tam3.Transition(inputs=["beg",], outputs=["end",], expression="2")
        inputms = tam3.Multisignal([("beg", 2)])
        outputms = trans.apply(inputms)
        outputmsexpec = tam3.Multisignal([("end", 2)])
        self.assertEqual(outputms, outputmsexpec)
    ##Property Function
    def test_applyProp(self):
        pf = tam3.PropertyFunction(inputs=["beg",], outputs=["end",], expression="2")
        inputms = tam3.Multisignal([("beg", 2)])
        outputms = tam3.Multisignal([("end", 2)])
        pfgiv = pf.apply(inputms, outputms)
        self.assertEqual(pfgiv, 2)
    ##Chooser Function
    def test_applyChoose(self):
        ch = tam3.ChooserFunction(inputNames=["name"], expression="2")
        inputms = tam3.Multisignal([("name",2)])
        tn = ch.apply(inputms)
        self.assertEqual(tn, (2,))
    def test_exptoFunc(self):
        tst = tam3.expressionToFunction(expression="2", inputNames="beg")
        val = tst("2","beg")
        self.assertEqual(val, 2)
    def test_ensIsFunc(self):
        tst = tam3.ensureIsFunction(expression="2", inputNames="beg", function=None, table=None)
        val = tst("2","beg")
        self.assertEqual(val, 2)
    def test_tableToFunc(self):
        tst = tam3.tableToFunction(table={1:2})
        with self.assertRaises(KeyError):
             val =tst(1)
    ##Tile Template Unit Tests
    def test_addAuxInput(self):
        mst = tam3.MultisignalType(signal = (0))
        tt = tam3.TileTemplate(name="tt")
        st = MultisignalType(tt.addAuxiliaryInput(mst))
        self.assertEqual(st.names(), [])
    def test_inputDirMsTypeDict(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsbIncBit = "0*")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        d = tt.inputDirMultisignalTypeDict()
        mst = (d[tam3.Direction.South])
        mspair = list(mst)[0]
        mspairstr = mspair.__str__()
        self.assertEqual(mspairstr, "seed1=s1")
    def test_outputDirMsTypeDict(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        d = tt.outputDirMultisignalTypeDict()
        mst = (d[tam3.Direction.West])
        mspair = list(mst)[0]
        mspairstr = mspair.__str__()
        self.assertEqual(mspairstr, "lsb=0")

    def test_inputDirMsTypeLst(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsbIncBit = "0*")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        d = tt.inputDirMultisignalTypeList()
        tuplepair = d[0]
        mspair = tuplepair[1]
        mspairstr = mspair.__str__()
        self.assertEqual(mspairstr, "seed1:('s1',)")

    def test_outputDirMsTypeLst(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        d = tt.outputDirMultisignalTypeList()
        tuplepair = d[0]
        mspair = tuplepair[1]
        mspairstr = mspair.__str__()
        self.assertEqual(mspairstr, "lsb:('0',)")
    def test_isInputSide(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        d = tt.isInputSide(tam3.Direction.South)
        self.assertEqual(d, True)
    def test_inputNeighborhood(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        with self.assertRaises(ValueError):
            d = tt.inputNeighborhood(tam3.Direction.West)
    def test_isOutputSide(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        d = tt.isOutputSide(tam3.Direction.West)
        self.assertEqual(d, True)
    def test_outputNeighborhood(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        with self.assertRaises(ValueError):
            d = tt.outputNeighborhood(tam3.Direction.South)
    def test_createTilesFromInputMs(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        mst = tam3.Multisignal([("lsb", 0)])
        with self.assertRaises(tam3.SignalInvalidValueError):
            to.createTilesFromInputMultisignal(mst)
    def test_createTileFromInputMs(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        mst = tam3.Multisignal([("lsb", 0)])
        with self.assertRaises(tam3.SignalInvalidValueError):
            to.createTileFromFullInputMultisignal(mst)
    def test_isValidInputMs(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        mst = tam3.Multisignal([("lsb", 0)])
        res = to.isValidInputMultisignal(mst)
        self.assertEqual(res, False)

    def test_inputMsType(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        res = tt.inputMultisignalType(tam3.Direction.South)
        resstr = res.__str__()
        self.assertEqual(resstr, "seed1:('s1',)")
    def test_removeTrans(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        with self.assertRaises(NonexistentTransitionError):
            res = tt.removeTransition("name")
    def test_numInputSides(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        res = tt.numInputSides()
        self.assertEqual(res, 1)
    def test_numOutputSides(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        res = tt.numOutputSides()
        self.assertEqual(res, 1)
    ##Neighborhood Unit Tests
    def test_combineNbrhd(self):
        nbrhd = tam3.Neighborhood(strength=1,direction=tam3.Direction.West)
        nbrhd2 = tam3.Neighborhood(strength=1,direction=tam3.Direction.West)
        rt = nbrhd.combine(nbrhd2)
        self.assertEqual(rt.strength, 1)
    ##ChooserSet Unit Tests
    def test_inputMst(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        chst = tam3.ChooserSet(tileSetTemplate= tst, tileTemplate= tt)
        ret = chst.inputMst
        retstr = ret.__str__()
        self.assertEqual(retstr, "seed1:('s1',)")
    def test_chooseTileTemp(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tr = tam3.TileTemplate(name="tr")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb1 = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        tst.join(2, tam3.Direction.North, tt, tr, lsb = "0")
        chst = tam3.ChooserSet(tileSetTemplate= tst, tileTemplate= tt)
        mst = tam3.Multisignal([("lsb", 0)])
        ret = chst.chooseTileTemplates(mst)
        self.assertEqual(ret,[])
    def test_findTileTempByName(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tr = tam3.TileTemplate(name="tr")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb1 = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        tst.join(2, tam3.Direction.North, tt, tr, lsb = "0")
        chst = tam3.ChooserSet(tileSetTemplate= tst, tileTemplate= tt)
        with self.assertRaises(TypeError):
            ret = chst.findTileTemplateByName("ti")

    def test_belongsInSet(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tr = tam3.TileTemplate(name="tr")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb1 = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        tst.join(2, tam3.Direction.North, tt, tr, lsb = "0")
        chst = tam3.ChooserSet(tileSetTemplate= tst, tileTemplate= tt)
        ret = chst.belongsInSet(to)
        self.assertEqual(ret, False)
    def test_isInSet(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tr = tam3.TileTemplate(name="tr")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb1 = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        tst.join(2, tam3.Direction.North, tt, tr, lsb = "0")
        chst = tam3.ChooserSet(tileSetTemplate= tst, tileTemplate= tt)
        ret = chst.isInSet(to)
        self.assertEqual(ret, False)
    def test_addTileTemp(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tr = tam3.TileTemplate(name="tr")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb1 = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        tst.join(2, tam3.Direction.North, tt, tr, lsb = "0")
        chst = tam3.ChooserSet(tileSetTemplate= tst, tileTemplate= tt)
        with self.assertRaises(ValueError):
            ret = chst.addTileTemplate(to)
    def test_addMultiSigVal(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tr = tam3.TileTemplate(name="tr")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb1 = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        tst.join(2, tam3.Direction.North, tt, tr, lsb = "0")
        chst = tam3.ChooserSet(tileSetTemplate= tst, tileTemplate= tt)
        with self.assertRaises(NameDifferenceError):
            ret = chst.addMultisignalValues(to)
    def test_removeTileTemp(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tr = tam3.TileTemplate(name="tr")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb1 = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        tst.join(2, tam3.Direction.North, tt, tr, lsb = "0")
        chst = tam3.ChooserSet(tileSetTemplate= tst, tileTemplate= tt)
        with self.assertRaises(ValueError):
            ret = chst.removeTileTemplate(to)
    ##Tile Set Template Unit Tests
    def test_errors(self):
        tst = tam3.TileSetTemplate()
        ret = tst.errors()
        self.assertEqual(ret, [])


    def test_addTile(self):
        tile = tam3.Tile(name = "tile", label='e',
                 tilecolor='white', textcolor='black', concentration=1,
                 northglue=('n', 1), southglue=('s', 1),
                 westglue=('w', 1), eastglue=('e', 1))
        tst = tam3.TileSetTemplate()
        tst.addTile(tile)
        self.assertEqual(len(tst.hardcodedTiles), 1)
    def test_ensureIsTemplate(self):
        tile = tam3.Tile(name = "tile1", label='e',
                 tilecolor='white', textcolor='black', concentration=1,
                 northglue=('n', 1), southglue=('s', 1),
                 westglue=('w', 1), eastglue=('e', 1))
        tst = tam3.TileSetTemplate()
        ret = tst.ensureIsTemplate(tile)
        self.assertEqual(ret.name, "tile1")
    def test_removeChooser(self):
        tst = tam3.TileSetTemplate()
        with self.assertRaises(NonexistentChooserSetError):
            tt = tam3.TileTemplate(name="red")
            tst.removeChooser(tt)
    def test_createTiles(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tr = tam3.TileTemplate(name="tr")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb1 = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        tst.join(2, tam3.Direction.North, tt, tr, lsb = "0")
        ret = tst.createTiles()
        retExpec = tam3.Tile(name="tt_East:lsb1=0", label="",tilecolor="white",textcolor="black",concentration=1,northglue=("seed1=s1;tt-N>tt",2), southglue=("",0), westglue=("",0), eastglue=("lsb1=0;tt-W>tt",2))
        self.assertEqual(ret[0], retExpec)
    def test_removeJoins(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tr = tam3.TileTemplate(name="tr")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb1 = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        tst.join(2, tam3.Direction.North, tt, tr, lsb = "0")
        ret = tst.removeJoin(strength =1, direction=tam3.Direction.West, fromTileTemplate=tt, toTileTemplate=to)
        self.assertEqual(ret, None)
    def test_getNeighborhoodForJoin(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tr = tam3.TileTemplate(name="tr")
        tst = tam3.TileSetTemplate()
        tst.join(2, tam3.Direction.West, tt, to, lsb1 = "0")
        tst.join(2, tam3.Direction.North, to, tt, seed1 = "s1")
        tst.join(2, tam3.Direction.North, tt, tr, lsb = "0")
        ret = tst._getNeighborhoodForJoin(strength = 2, direction=tam3.Direction.West, fromTileTemplate=tt, toTileTemplate=to)
        self.assertEqual(ret.multisignalType.__str__(), "lsb1:('0',)")
    def test_join(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="tt")
        tr = tam3.TileTemplate(name="tr")
        tst = tam3.TileSetTemplate()
        ret = tst.join(2, tam3.Direction.West, tt, to, lsb = "0")
        self.assertEqual(ret.multisignalType.__str__(),"lsb:('0',)")
    def test_ModJoinTT(self):
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")
        tst = tam3.TileSetTemplate()
        rootMod = tam3.Module("root")
        rootMod.add(t1)
        rootMod.add(t2)
        rootMod.add(t3)
        rootMod.join(2,tam3.Direction.East, t1, t2,tst, bit = [0,1])
        rootMod.join(2,tam3.Direction.East, t1, t3,tst, bit=[1,2])
        ms = t1.outputDirMultisignalTypeList()
        tuplepairs = ms[0]
        msfort1 = tuplepairs[1]
        expectedms = tam3.MultisignalType(bit = [0,1,2])
        self.assertEqual(msfort1, expectedms)
    def test_ModJoinTP(self):
        tst = tam3.TileSetTemplate()
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        rootMod = tam3.Module("root")
        port = tam3.Port("port")
        rootMod.add(t1)
        rootMod.add(t2)
        rootMod.add_port(port, tam3.Direction.East)
        rootMod.join(2,tam3.Direction.East, t1, port,tst, bit = [0,1])
        rootMod.join(2,tam3.Direction.East, t2, port,tst, bit=[1,2])
        portmt = port.inputJoins[0].multisignalType
        portmt2 = port.inputJoins[1].multisignalType
        expectedms1 = tam3.MultisignalType(bit = [0,1])
        expectedms2 = tam3.MultisignalType(bit = [1,2])
        self.assertEqual(portmt, expectedms1)
        self.assertEqual(portmt2, expectedms2)
    def test_ModJoinTP_PortInSubModule(self):
        tst = tam3.TileSetTemplate()
        t1 = tam3.TileTemplate("t1")
        rootMod = tam3.Module("root")
        portMod = tam3.Module("portMod")
        port = tam3.Port("port")
        rootMod.add(t1)
        rootMod.add(portMod)
        portMod.add_port(port, tam3.Direction.North)
        portMod.join(2, tam3.Direction.South, t1, port,tst, carry = [0,5,7])
        portmt = port.inputJoins[0].multisignalType
        expectedms1 = tam3.MultisignalType(carry = [0,5,7])
        self.assertEqual(portmt, expectedms1)
    def test_ModJoinPT(self):
        tst = tam3.TileSetTemplate()
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        rootMod = tam3.Module("root")
        port = tam3.Port("port")
        rootMod.add(t1)
        rootMod.add(t2)
        rootMod.add_port(port, tam3.Direction.East)
        rootMod.join(2,tam3.Direction.East, port, t1,tst, bit = [0,1])
        rootMod.join(2,tam3.Direction.East, port, t2,tst, bit=[1,2])
        portmt = port.outputJoins[0].multisignalType
        portmt2 = port.outputJoins[1].multisignalType
        portlist = port.outputDirMultisignalTypeDict()
        expectedms1 = tam3.MultisignalType(bit = [0,1])
        expectedms2 = tam3.MultisignalType(bit = [1,2])
        self.assertEqual(portmt, expectedms1)
        self.assertEqual(portmt2, expectedms2)
    def test_ModJoinPT_TtInSubmodule(self):
        tst = tam3.TileSetTemplate()
        t1 = tam3.TileTemplate("t1")
        rootMod = tam3.Module("root")
        subMod = tam3.Module("subMod")
        port = tam3.Port("port")
        rootMod.add_port(port, tam3.Direction.South)
        rootMod.add(subMod)
        subMod.add(t1)
        subMod.join(2, tam3.Direction.South, port, t1,tst, carry = [0,5,7])
        portmt = port.outputJoins[0].multisignalType
        expectedms1 = tam3.MultisignalType(carry = [0,5,7])
        self.assertEqual(portmt, expectedms1)
    def test_ModJoinPP(self):
        tst = tam3.TileSetTemplate()
        p1 = tam3.Port("p1")
        p2 = tam3.Port("p2")
        rootMod = tam3.Module("root")
        p1Mod = tam3.Module("p1Mod")
        p2Mod = tam3.Module("p2Mod")
        rootMod.add(p1Mod)
        rootMod.add(p2Mod)
        p1Mod.add_port(p1, tam3.Direction.East)
        p2Mod.add_port(p2, tam3.Direction.West)
        rootMod.join(2, tam3.Direction.East, p1, p2,tst, right = ["a","b"])
        portmt = p1.outputJoins[0].multisignalType
        expectedms = tam3.MultisignalType( right = ["a","b"])
        self.assertEqual(portmt, expectedms)
    def test_ModJoinPP_P2InSubModFrom(self):
        tst = tam3.TileSetTemplate()
        rootmod = tam3.Module("root")
        subMod1 = tam3.Module("s1")
        subMod2 = tam3.Module("s2")
        rootmod.add(subMod1)
        subMod1.add(subMod2)
        p1 =tam3.Port("p1")
        p2 = tam3.Port("p2")
        subMod1.add_port(p1, tam3.Direction.East)
        subMod2.add_port(p2, tam3.Direction.East)
        subMod2.join(2, tam3.Direction.East, p2, p1,tst, bit = [0,1])
        portmt = p2.outputJoins[0].multisignalType
        expectedms = tam3.MultisignalType( bit = [0,1])
        self.assertEqual(portmt, expectedms)
    def test_ModJoinPP_P2InSubModTo(self):
        tst = tam3.TileSetTemplate()
        rootmod = tam3.Module("root")
        subMod1 = tam3.Module("s1")
        subMod2 = tam3.Module("s2")
        rootmod.add(subMod1)
        subMod1.add(subMod2)
        p1 =tam3.Port("p1")
        p2 = tam3.initiatorPort("p2", 1, True)
        subMod1.add_port(p1, tam3.Direction.East)
        subMod2.add_port(p2, tam3.Direction.East)
        subMod2.join(2, tam3.Direction.East, p1, p2,tst, bit = [0,1])
        portmt = p2.inputJoins[0].multisignalType
        expectedms = tam3.MultisignalType( bit = [0,1])
        self.assertEqual(portmt, expectedms)
    def test_ModJoinTPError(self):
        tst = tam3.TileSetTemplate()
        rootMod = tam3.Module("root")
        subMod = tam3.Module("subMod")
        rootMod.add(subMod)
        subMod2 = tam3.Module("subMod2")
        subMod.add(subMod2)
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        subMod.add(t1)
        subMod2.add(t2)
        with self.assertRaises(tam3.TileTemplateFromObjNotConfomingtoModuleConfigurationError):
            subMod.join(2, tam3.Direction.West, t2, t1,tst, test = "a")
    def test_ModJoinPTError(self):
        tst = tam3.TileSetTemplate()
        rootMod = tam3.Module("root")
        subMod = tam3.Module("subMod")
        rootMod.add(subMod)
        subMod2 = tam3.Module("subMod2")
        subMod.add(subMod2)
        t1 = tam3.TileTemplate("t1")
        p2 = tam3.Port("p2")
        subMod.add(t1)
        subMod2.add_port(p2, tam3.Direction.East)
        with self.assertRaises(tam3.PortFromObjNotConformingtoModuleConfigurationError):
            subMod.join(2, tam3.Direction.West, p2, t1,tst, test = "a")

    def test_TestJOinTest(self):
        rootMod = tam3.Module("root")
        tst = tam3.TileSetTemplate()
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        rootMod.add(t1)
        rootMod.add(t2)
        ret = rootMod.join(2, tam3.Direction.East, t1, t2, tst, lsb = "0")
        self.assertEqual(ret.multisignalType.__str__(),"lsb:('0',)")



    def test_inputPortConnectToTileError(self):
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")
        t4 = tam3.TileTemplate("t4")
        t5 = tam3.TileTemplate("t5")
        p1 = tam3.Port("p1")
        p2 = tam3.Port("p2")
        p3 = tam3.Port("p3")
        rootMod = tam3.Module("root")
        m1 = tam3.Module("m1")
        m2 = tam3.Module("m2")
        tst = tam3.TileSetTemplate()
        rootMod.add(m1)
        rootMod.add(m2)
        m1.add_port(p1, tam3.Direction.East)
        m2.add_port(p2, tam3.Direction.West)
        m2.add_port(p3, tam3.Direction.South)
        rootMod.add(t5)
        m1.add(t1)
        m1.add(t2)
        m2.add(t3)
        m2.add(t4)
        ##m1.join(2, tam3.Direction.West, t1, t2, tst, test="1")
        m1.join(2, tam3.Direction.West, t1, p1, tst, test="1")
        rootMod.join(2, tam3.Direction.West, p1, p2, tst, test="2")
        #rootMod.join(2, tam3.Direction.West, t5, p2, tst, test="2")
        m2.join(2, tam3.Direction.West, p2, t3, tst, test="4")
        m2.join(2, tam3.Direction.West, p2, t4, tst, test="4")
        m2.join(2, tam3.Direction.South, t4, p3, tst, test="5")
        with self.assertRaises(tam3.portsNotConnectedToTileTemplatesInput):
            tst.ensurePortToTileInputSide()
    def test_raisesIniatorPortError(self):

        root = tam3.Module("root")
        initiatorPort1 = tam3.initiatorPort("iP1",1, True)
        initiatorPort2 = tam3.initiatorPort("iP2",2, True)
        root.add_port(initiatorPort1, tam3.Direction.South)
        with self.assertRaises(tam3.tooManyInitatiorPortsError):
            root.add_port(initiatorPort2, tam3.Direction.South)
    #createTiles is a success
    def test_ModuleCreateTiles(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="to")
        tr = tam3.TileTemplate(name="tr")
        ts = tam3.TileTemplate(name="tS")
        ta = tam3.TileTemplate(name="ta")
        tst = tam3.TileSetTemplate()
        rootMod = tam3.Module("rootMod")
        rootMod.add(tt)
        rootMod.add(to)
        rootMod.add(tr)
        rootMod.add(ts)
        rootMod.add(ta)
        rootMod.join(2, tam3.Direction.West, tt, to, tst, lsb1 = "0")
        rootMod.join(2, tam3.Direction.North, to, tt, tst,  seed1 = "s1")
        rootMod.join(1, tam3.Direction.North, tt, tr, tst, lsb = "0")
        rootMod.join(1, tam3.Direction.North, ts, tr, tst, lsb = "1")
        rootMod.join(1, tam3.Direction.North, ts, ta, tst, lsb = "2")

        ret = rootMod.createTiles(tst)

        retExpec = tam3.Tile(name="to_East:lsb1=0", label="",tilecolor="white",textcolor="black",concentration=1,northglue=("seed1=s1;to-N>tt-rootMod",2), southglue=("",0), westglue=("",0), eastglue=("lsb1=0;tt-W>to-rootMod",2))
        self.assertEqual(ret[0], retExpec)

    #West
    def test_ModuleCreateTilesWithPortsWest(self):
        tt = tam3.TileTemplate(name="tt")
        to = tam3.TileTemplate(name="to")
        tst = tam3.TileSetTemplate()
        ts = tam3.TileTemplate(name="TS")
        tr = tam3.TileTemplate(name="tR")
        rootMod = tam3.Module("rootMod")
        m1 = tam3.Module("m1")
        m2 = tam3.Module("m2")
        p1 = tam3.initiatorPort("p1", 2, False)
        ip1 = tam3.initiatorPort('ip1',2, True)
        rootMod.add(m1)
        rootMod.add(m2)
        m1.add(ts)
        m1.add(tr)
        m1.add_port(p1, tam3.Direction.West)
        m1.add(tt)
        m2.add(to)
        m2.add_port(ip1, tam3.Direction.West)
        p2 = tam3.Port("PP2")
        m2.add_port(p2, tam3.Direction.West)
        m1.join(2, tam3.Direction.West, ts, tt, tst, tstt = "2")
        m1.join(2, tam3.Direction.West, tt, p1, tst, lsb1 = "0")
        m1.join(2, tam3.Direction.West, tr, p1, tst, lsb1 = "0")
        rootMod.join(2, tam3.Direction.West, p1, ip1, tst, lsb1 = "0")
        m2.join(2, tam3.Direction.West, ip1, to, tst,  lsb1 = "0")
        ttTile = m1.createTiles(tst)[0]
        retWestGlue = ttTile.westglue
        expWestGlue = ("lsb1=0;ip1,p1,tR,tt-W>to-rootMod", 2)
        self.assertEqual(retWestGlue, expWestGlue)



    #East
    def test_ModuleCreateTilesWithPortsEast(self):
        tst = tam3.TileSetTemplate()
        ts = tam3.TileTemplate("ts")
        ti = tam3.TileTemplate("TI")
        t1 = tam3.TileTemplate("t1")
        p1 = tam3.Port("p1")
        p2 = tam3.Port("p2")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")
        rootMod = tam3.Module("rootMod")
        m1 = tam3.Module("m1")
        m2 = tam3.Module("m2")
        m1.add(t3)
        rootMod.add(m1)
        rootMod.add(m2)
        m1.add(ts)
        m1.add(ti)
        m1.add(t1)
        m1.add_port(p1, tam3.Direction.East)
        m2.add_port(p2, tam3.Direction.East)
        m2.add(t2)
        m1.join(2, tam3.Direction.North, ts, ti, tst, up = "0")
        m1.join(2, tam3.Direction.East, ti, t1, tst, side = "1")
        m1.join(2, tam3.Direction.East, t1, p1, tst, portPass = "1")
        m1.join(2, tam3.Direction.East, t3, p1, tst, portPass = "1")
        rootMod.join(2, tam3.Direction.East, p1, p2, tst, portPass = "1")
        m2.join(2, tam3.Direction.East, p2, t2, tst, portPass = "1")
        ttTile = m1.createTiles(tst)[1]
        retEastGlue = ttTile.eastglue
        expEastGlue = ("portPass=1;p1,p2,t1,t3-E>t2-rootMod", 2)
        self.assertEqual(retEastGlue, expEastGlue)

    #North
    def test_ModuleCreateTilesWithPortsNorth(self):

        tst = tam3.TileSetTemplate()
        ts = tam3.TileTemplate("ts")
        ti = tam3.TileTemplate("TI")
        t1 = tam3.TileTemplate("t1")
        p1 = tam3.Port("p1")
        p2 = tam3.Port("p2")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")
        rootMod = tam3.Module("rootMod")
        m1 = tam3.Module("m1")
        m2 = tam3.Module("m2")
        m1.add(t3)
        rootMod.add(m1)
        rootMod.add(m2)
        m1.add(ts)
        m1.add(ti)
        m1.add(t1)
        m1.add_port(p1, tam3.Direction.North)
        m2.add_port(p2, tam3.Direction.North)
        m2.add(t2)
        m1.join(2, tam3.Direction.West, ts, ti, tst, up = "0")
        m1.join(2, tam3.Direction.North, ti, t1, tst, side = "1")
        m1.join(2, tam3.Direction.North, t1, p1, tst, portPass = "1")
        m1.join(2, tam3.Direction.North, t3, p1, tst, portPass = "1")
        rootMod.join(2, tam3.Direction.North, p1, p2, tst, portPass = "1")
        m2.join(2, tam3.Direction.North, p2, t2, tst, portPass = "1")
        ttTile = m1.createTiles(tst)[1]
        retNorthGlue = ttTile.northglue
        expNorthGlue = ("portPass=1;p1,p2,t1,t3-N>t2-rootMod", 2)
        self.assertEqual(retNorthGlue, expNorthGlue)


    #South
    def test_ModuleCreateTilesWithPortsSouth(self):

        tst = tam3.TileSetTemplate()
        ts = tam3.TileTemplate("ts")
        ti = tam3.TileTemplate("TI")
        t1 = tam3.TileTemplate("t1")
        p1 = tam3.Port("p1")
        p2 = tam3.Port("p2")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")
        rootMod = tam3.Module("rootMod")
        m1 = tam3.Module("m1")
        m2 = tam3.Module("m2")
        m1.add(t3)
        rootMod.add(m1)
        rootMod.add(m2)
        m1.add(ts)
        m1.add(ti)
        m1.add(t1)
        m1.add_port(p1, tam3.Direction.South)
        m2.add_port(p2, tam3.Direction.South)
        m2.add(t2)
        m1.join(2, tam3.Direction.West, ts, ti, tst, up = "0")
        m1.join(2, tam3.Direction.South, ti, t1, tst, side = "1")
        m1.join(2, tam3.Direction.South, t1, p1, tst, portPass = "1")
        m1.join(2, tam3.Direction.South, t3, p1, tst, portPass = "1")
        rootMod.join(2, tam3.Direction.South, p1, p2, tst, portPass = "1")
        m2.join(2, tam3.Direction.South, p2, t2, tst, portPass = "1")
        ttTile = m1.createTiles(tst)[1]
        retSouthGlue = ttTile.southglue
        expSouthGlue = ("portPass=1;p1,p2,t1,t3-S>t2-rootMod", 2)
        self.assertEqual(retSouthGlue, expSouthGlue)

    def test_ModuleCreateTilesWithMultiLevelPorts(self):
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")
        p1 = tam3.Port("p1")
        p2 = tam3.Port("p2")
        p3 = tam3.Port("p3")
        p4 = tam3.Port("p4")
        rootMod = tam3.Module("rootMod")
        m1 = tam3.Module("m1")
        m2 = tam3.Module("m2")
        m3 = tam3.Module("m3")
        m4 = tam3.Module("m4")
        tst = tam3.TileSetTemplate()
        rootMod.add(m2)
        rootMod.add(m3)
        m2.add(m1)
        m3.add(m4)
        m1.add(t1)
        m1.add(t2)
        m4.add(t3)
        m1.add_port(p1, tam3.Direction.South)
        m2.add_port(p2, tam3.Direction.South)
        m3.add_port(p3, tam3.Direction.South)
        m4.add_port(p4, tam3.Direction.South)
        m1.join(1, tam3.Direction.South, t1, t2, tst, tT = "3")
        m1.join(1, tam3.Direction.South, t2, p1, tst, pP = "2")
        m2.join(1, tam3.Direction.South, p1, p2, tst, pP = "2")
        rootMod.join(1, tam3.Direction.South, p2, p3, tst, pP = "2")
        m3.join(1, tam3.Direction.South, p3, p4, tst, pP = "2")
        m4.join(1, tam3.Direction.South, p4, t3, tst, pP = "2")
        ttTile = m1.createTiles(tst)[0]
        retSouthGlue = ttTile.southglue
        expSouthGlue = ("pP=2;p1,p2,p3,p4,t2-S>t3-rootMod", 1)
        self.assertEqual(retSouthGlue, expSouthGlue)
    def test_ModuleCreateTilesWithMultiLevelPortsAncestor(self):
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")
        p1 = tam3.Port("p1")
        p2 = tam3.Port("p2")
        p3 = tam3.Port("p3")
        p4 = tam3.Port("p4")
        rootMod = tam3.Module("rootMod")
        subRootMod = tam3.Module("subRootMod")
        m1 = tam3.Module("m1")
        m2 = tam3.Module("m2")
        m3 = tam3.Module("m3")
        m4 = tam3.Module("m4")
        tst = tam3.TileSetTemplate()
        rootMod.add(subRootMod)
        subRootMod.add(m2)
        subRootMod.add(m3)
        m2.add(m1)
        m3.add(m4)
        m1.add(t1)
        m1.add(t2)
        m4.add(t3)
        m1.add_port(p1, tam3.Direction.South)
        m2.add_port(p2, tam3.Direction.South)
        m3.add_port(p3, tam3.Direction.South)
        m4.add_port(p4, tam3.Direction.South)
        m1.join(1, tam3.Direction.South, t1, t2, tst, tT = "3")
        m1.join(1, tam3.Direction.South, t2, p1, tst, pP = "2")
        m2.join(1, tam3.Direction.South, p1, p2, tst, pP = "2")
        subRootMod.join(1, tam3.Direction.South, p2, p3, tst, pP = "2")
        m3.join(1, tam3.Direction.South, p3, p4, tst, pP = "2")
        m4.join(1, tam3.Direction.South, p4, t3, tst, pP = "2")
        ttTile = m1.createTiles(tst)[0]
        retSouthGlue = ttTile.southglue
        expSouthGlue = ("pP=2;p1,p2,p3,p4,t2-S>t3-rootMod,subRootMod", 1)
        self.assertEqual(retSouthGlue, expSouthGlue)

    def test_ModuleJoinWithTransitions(self):
        rootMod = tam3.Module("rootMod")
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")
        t4 = tam3.TileTemplate("t4")
        tst = tam3.TileSetTemplate()
        rootMod.add(t1)
        rootMod.add(t2)
        rootMod.add(t3)
        rootMod.add(t4)

        rootMod.join(1, tam3.Direction.North, t1, t3, tst, up = (0,1))
        rootMod.join(1, tam3.Direction.East, t2, t3, tst, east = (0,1))
        rootMod.join(2,tam3.Direction.North, t3, t4, tst, fn = (2,3))

        t3.addTransition(inputs=("up","east"), outputs=("fn"),table={(0,0):(2), (0,1):(2), (1,0):(3), (1,1):(3)})

        tiles = rootMod.createTiles(tst)

        retTile = tiles[0]
        retTileNorthGlue = retTile.northglue
        retTileSouthGlue = retTile.southglue
        retTileWestGlue = retTile.westglue

        expNorthGlue = ("fn=2;t3-N>t4-rootMod", 2)
        expSouthGlue = ("up=0;t1-N>t3-rootMod", 1)
        expWestGlue = ("east=0;t2-E>t3-rootMod", 1)
        self.assertEqual(retTileSouthGlue, expSouthGlue)
        self.assertEqual(retTileNorthGlue, expNorthGlue)
        self.assertEqual(retTileWestGlue, expWestGlue)


    def test_createTilesTTModules(self):
        N = tam3.Direction.North
        S = tam3.Direction.South
        E = tam3.Direction.East
        W = tam3.Direction.West
        tst = tam3.TileSetTemplate()
        rootMod = tam3.Module("rootMod")
        bottomRightSquareMod = tam3.Module("bottomRightSquareMod")
        msbBotRight = tam3.TileTemplate("msbBotRight")
        lsbBotRight = tam3.TileTemplate("lsbBotRight")
        intBotRight = tam3.TileTemplate("intBotRight")
        fillerH = tam3.TileTemplate(name="fillerH")
        fillerG = tam3.TileTemplate(name="fillerG")
        topH = tam3.TileTemplate(name="topH")
        topG = tam3.TileTemplate(name="topG")
        intBotRightFill = tam3.TileTemplate(name="intBotRightFill")
        msbBotRightFill = tam3.TileTemplate(name="msbBotRightFill")
        rootMod.add(bottomRightSquareMod)

        bottomRightSquareMod.add(msbBotRight)
        bottomRightSquareMod.add(lsbBotRight)
        bottomRightSquareMod.add(intBotRight)
        bottomRightSquareMod.add(fillerG)
        bottomRightSquareMod.add(fillerH)
        bottomRightSquareMod.add(topG)
        bottomRightSquareMod.add(topH)
        bottomRightSquareMod.add(intBotRightFill)
        bottomRightSquareMod.add(msbBotRightFill)
        bottomRightSquareMod.join(2, S, msbBotRight, topG, tst, gSig = "G")
        bottomRightSquareMod.join(1, S, intBotRight, topH,tst, hFill = "h")
        bottomRightSquareMod.join(1, S, intBotRight, fillerH,tst, hFill = "h")
        bottomRightSquareMod.join(2, S, topH, topG,tst, gSig = "G")
        bottomRightSquareMod.join(1, W, topG, topH,tst, iSig = "i")
        bottomRightSquareMod.join(1, S, topG, fillerG,tst, gFill = "g")
        bottomRightSquareMod.join(1, E, topG, fillerG,tst, gFillHoriz = "g")
        bottomRightSquareMod.join(1, S, fillerG, fillerG, tst, gFill = "g")
        bottomRightSquareMod.join(1, E, fillerG, fillerG,tst, gFillHoriz = "g")
        bottomRightSquareMod.join(1, S, fillerH, topH,tst, hFill = "h")
        bottomRightSquareMod.join(1, W, topH, fillerH,tst, hFillHoriz = "h")
        bottomRightSquareMod.join(1, S, fillerH, fillerH,tst, hFill = "h")
        bottomRightSquareMod.join(1, W, fillerH, fillerH,tst, hFillHoriz = "h")
        bottomRightSquareMod.join(1, W, fillerH, intBotRightFill,tst, hFillHoriz = "h")
        bottomRightSquareMod.join(1, W, topH, intBotRightFill,tst, hFillHoriz = "h")
        bottomRightSquareMod.join(1, W, topG, msbBotRightFill,tst, iSig = "i")
        bottomRightSquareMod.join(1, S, lsbBotRight, intBotRightFill, tst, lMS = 0)
        bottomRightSquareMod.join(1, S, intBotRightFill, intBotRightFill, tst, lMS = 0)
        bottomRightSquareMod.join(1, S, intBotRightFill, msbBotRightFill, tst, lMS = 0)

        tiles5 = bottomRightSquareMod.createTiles(tst)
        tileSystem5 = tam3.TileSystem("unitTestTest", tiles5)
        tileSystem5.writeToFiles('unitTestTest')

    def test_portWithMultiInput(self):
        N = tam3.Direction.North
        S = tam3.Direction.South
        E = tam3.Direction.East
        W = tam3.Direction.West
        tst = tam3.TileSetTemplate()
        rootMod = tam3.Module("rootMod")
        firstMod = tam3.Module("firtMod")
        secondMod = tam3.Module("secondMod")

        p1 = tam3.Port("p1")
        p2 = tam3.Port("p2")

        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")

        rootMod.add(firstMod)
        rootMod.add(secondMod)
        firstMod.add(t1)
        firstMod.add(t2)
        firstMod.add_port(p1, N)
        secondMod.add_port(p2, S)
        secondMod.add(t3)

        firstMod.join(2, N, t1, t2, tst, up = ("0","1"))
        firstMod.join(2, N, t2, p1, tst, test = ("1","2"))

        rootMod.join(2, N, p1, p2, tst, test = ("1","2"))

        secondMod.join(2, N, p2, t3, tst, test = ("1","2"))
        t2.addTransition(inputs=("up"), outputs=("test"),table={("0",):("1"), ("1",):("2")})


        tile2 = secondMod.createTiles(tst)
        tile1 = firstMod.createTiles(tst)


        tileSystem1 = tam3.TileSystem("multiPort1",tile1)

        tileSystem1.writeToFiles('multiPort1')

        tileSystem2 = tam3.TileSystem("multiPort2",tile2)

        tileSystem2.writeToFiles('multiPort2')


    #one to see that copies are same
    def test_copyModule(self):
        rootMod = tam3.Module("rootMod")
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")
        t4 = tam3.TileTemplate("t4")
        t5 = tam3.TileTemplate("t5")
        t6 = tam3.TileTemplate("t6")
        tst = tam3.TileSetTemplate()
        rootMod.add(t1)
        rootMod.add(t2)
        rootMod.add(t3)
        rootMod.add(t4)


        rootMod.join(2, tam3.Direction.North, t1, t3, tst, up = (1))
        rootMod.join(2, tam3.Direction.East, t1, t2, tst, east = (1))
        rootMod.join(2,tam3.Direction.North, t3, t4, tst, fn = (3))


        cpRootMod = rootMod.copyModule(tst)
        cpRootMod.renameModule("copiedMod")

        tiles = len(rootMod.tile_templates)

        tiles1 = len(cpRootMod.tile_templates)
        self.assertEqual(tiles, tiles1)


    #one to see that change in origional does not affect the copy


    def test_copyModuleOrigDoesntAffectCopy(self):
        rootMod = tam3.Module("rootMod")
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")
        t4 = tam3.TileTemplate("t4")
        t5 = tam3.TileTemplate("t5")
        t6 = tam3.TileTemplate("t6")
        t7 = tam3.TileTemplate("t7")
        p1 = tam3.Port("p1")
        p2 = tam3.Port("p2")
        tst = tam3.TileSetTemplate()
        subMod = tam3.Module("subMod")
        rootMod.add(subMod)
        subMod.add(t1)
        subMod.add(t2)
        subMod.add(t3)
        subMod.add(t4)



        subMod.join(2, tam3.Direction.North, t1, t3, tst, up = (1))
        subMod.join(2, tam3.Direction.East, t1, t2, tst, east = (1))
        subMod.join(2,tam3.Direction.North, t3, t4, tst, fn = (3))


        cpSubMod = subMod.copyModule(tst)
        cpSubMod.renameModule("copiedSubMod")
        rootMod.add(cpSubMod)
        #see what happens when add tile templates


        subMod.add(t5)
        subMod.add(t6)

        cpSubMod.add(t7)
        #all chooserset tileset are same as the tiletemplates in the module that the chooserset has all necessary info with it

        for chooserSet in cpSubMod.chooserSets:

            for tile in chooserSet.tileSet:
            #not seeing it as a tile template almost?
                if tile.name == "t3":

                    tileSett3 = tile

            if chooserSet.tileTemplate.name == "t3":

                chooserT3 = chooserSet.tileTemplate

        newT3 = None
        for tileTemplate in cpSubMod.tile_templates:
            if tileTemplate.name == "t3":
                newT3 = tileTemplate
        newT4 = None
        for tileTemplate in cpSubMod.tile_templates:
            if tileTemplate.name == "t4":
                newT4 = tileTemplate

        subMod.add_port(p2, tam3.Direction.North)
        cpSubMod.add_port(p1, tam3.Direction.North)
        cpSubMod.join(2, tam3.Direction.North, newT4, p1, tst, newPortSig = (7))

        rootMod.join(2, tam3.Direction.North, p1, p2, tst, newPortSig = (7))

        subMod.join(2, tam3.Direction.North, p2, t1, tst, newPortSig = (7))

        subMod.join(2,tam3.Direction.North, t4, t5, tst, upper = (4))
        subMod.join(2,tam3.Direction.North, t5, t6, tst, realupper = (5))






        self.assertEqual(chooserT3, newT3)
        self.assertEqual(tileSett3, chooserT3)
        tiles = subMod.createTiles(tst)

        tiles1 = cpSubMod.createTiles(tst)

        self.assertNotEqual(tiles, tiles1)

        #self.assertNotEqual(tiles, tiles1)


    def test_tileTemplateCloneFunction(self):
        rootMod = tam3.Module("rootMod")
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")
        tst = tam3.TileSetTemplate()
        subMod = tam3.Module("subMod")
        difMod = tam3.Module("difMod")
        rootMod.add(subMod)
        subMod.add(t1)
        subMod.add(t2)
        subMod.add(t3)




        subMod.join(2, tam3.Direction.North, t1, t2, tst, up = (1))
        subMod.join(2, tam3.Direction.North, t2, t3, tst, tstFunc = (1))

        cpT2 = t2.clone()

        cpT2.parent = difMod



        self.assertNotEqual(cpT2, t2)




    def test_areTheChooserSetsStillTheSame(self):
        rootMod = tam3.Module("rootMod")
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")
        t4 = tam3.TileTemplate("t4")
        t5 = tam3.TileTemplate("t5")
        t6 = tam3.TileTemplate("t6")
        t7 = tam3.TileTemplate("t7")
        tst = tam3.TileSetTemplate()
        subMod = tam3.Module("subMod")
        rootMod.add(subMod)
        subMod.add(t1)
        subMod.add(t2)
        subMod.add(t3)
        subMod.add(t4)



        subMod.join(2, tam3.Direction.North, t1, t3, tst, up = (1))
        subMod.join(2, tam3.Direction.East, t1, t2, tst, east = (1))
        subMod.join(2,tam3.Direction.North, t3, t4, tst, fn = (3))


        cpSubMod = subMod.copyModule(tst)
        cpSubMod.renameModule("copiedSubMod")


        subChooserSet = subMod.chooserSets[0]
        cpChooserSet = cpSubMod.chooserSets[0]

        self.assertNotEqual(subChooserSet, cpChooserSet)



    #try it with the insital connected to a different moduel then the copied connected to the end of that module
    def test_portToCopiedModule(self):
        rootMod = tam3.Module("rootMod")
        subMod = tam3.Module("subMod")
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")
        t4 = tam3.TileTemplate("t4")
        t5 = tam3.TileTemplate("t5")
        t6 = tam3.TileTemplate("t6")
        t7 = tam3.TileTemplate("t7")
        tst = tam3.TileSetTemplate()
        subMod.add(t1)
        subMod.add(t2)
        subMod.add(t3)
        subMod.add(t4)
        subMod.add(t5)
        subMod.add(t6)
        subMod.add(t7)


        subMod.join(2, tam3.Direction.East, t1, t2, tst, t1East = 0)
        subMod.join(2, tam3.Direction.East, t2, t3, tst, t2East = 0)
        subMod.join(2, tam3.Direction.East, t3, t4, tst, t3East = 0)
        subMod.join(2, tam3.Direction.North, t1, t5, tst, t1North = 0)
        subMod.join(1, tam3.Direction.North, t2, t6, tst, t23North = 0)
        subMod.join(1, tam3.Direction.North, t3, t6, tst, t23North = 0)
        subMod.join(1, tam3.Direction.North, t4, t7, tst, t4North = 0)
        subMod.join(1, tam3.Direction.East, t5, t6, tst, t5East = 0)
        subMod.join(1, tam3.Direction.East, t6, t6, tst, t5East = 0)
        subMod.join(1, tam3.Direction.East, t6, t7, tst, t5East = 0)

        cpSubMod = subMod.copyModule(tst)
        rootMod.add(cpSubMod)
        rootMod.add(subMod)
        cpSubMod.renameModule("copiedSubMod")

        subModPortLeft = tam3.Port("subModPortLeft")
        subModPortMid = tam3.Port("subModPortMid")
        subModPortRight = tam3.Port("subModPortRight")
        cpSubModPortLeft = tam3.Port("cpSubModPortLeft")
        cpSubModPortMid = tam3.Port("cpSubModPortMid")
        cpSubModPortRight = tam3.Port("cpSubModPortRight")

        subMod.add_port(subModPortLeft, tam3.Direction.North)
        subMod.add_port(subModPortMid, tam3.Direction.North)
        subMod.add_port(subModPortRight, tam3.Direction.North)
        cpSubMod.add_port(cpSubModPortLeft, tam3.Direction.North)
        cpSubMod.add_port(cpSubModPortMid, tam3.Direction.North)
        cpSubMod.add_port(cpSubModPortRight, tam3.Direction.North)

        subMod.join(2, tam3.Direction.North, t5, subModPortLeft, tst, subToPortL = 0)
        subMod.join(1, tam3.Direction.North, t6, subModPortMid, tst, subToPortM = 0)
        subMod.join(1, tam3.Direction.North, t7, subModPortRight, tst, subToPortR = 0)

        rootMod.join(2, tam3.Direction.North, subModPortLeft, cpSubModPortLeft, tst, subToPortL = 0)
        rootMod.join(1, tam3.Direction.North, subModPortMid, cpSubModPortMid, tst, subToPortM = 0)
        rootMod.join(1, tam3.Direction.North, subModPortRight, cpSubModPortRight, tst, subToPortR = 0)


        cpT1 = cpSubMod.tile_templates[0]
        cpT2 = cpSubMod.tile_templates[1]
        cpT3 = cpSubMod.tile_templates[2]
        cpT4 = cpSubMod.tile_templates[3]

        cpSubMod.join(2, tam3.Direction.North, cpSubModPortLeft, cpT1, tst, subToPortL = 0)
        cpSubMod.join(1, tam3.Direction.North, cpSubModPortMid, cpT2, tst, subToPortM = 0)
        cpSubMod.join(1, tam3.Direction.North, cpSubModPortMid, cpT3, tst, subToPortM = 0)
        cpSubMod.join(1, tam3.Direction.North, cpSubModPortRight, cpT4, tst, subToPortR = 0)

        tiles = subMod.createTiles(tst)
        tiles1 = cpSubMod.createTiles(tst)
        tileSystem = tam3.TileSystem("subModNew",tiles)
        tileSystem.writeToFiles("subModNew")
        tileSystem = tam3.TileSystem("cpSubModNew",tiles1)
        tileSystem.writeToFiles("cpSubModNew")

    def test_rotateModuleClockwise(self):
        rootMod = tam3.Module("rootMod")
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")
        t4 = tam3.TileTemplate("t4")
        t5 = tam3.TileTemplate("t5")
        t6 = tam3.TileTemplate("t6")
        t7 = tam3.TileTemplate("t7")
        tst = tam3.TileSetTemplate()
        subMod = tam3.Module("subMod")
        rootMod.add(subMod)
        subMod.add(t1)
        subMod.add(t2)
        subMod.add(t3)
        subMod.add(t4)
        subMod.add(t5)
        subMod.add(t6)
        subMod.add(t7)

        #all wrong joins are getting rotated counter clockwise instead of clockwise

        subMod.join(2, tam3.Direction.North, t1, t3, tst, up = (1))
        subMod.join(2, tam3.Direction.East, t1, t2, tst, east = (1))
        subMod.join(2,tam3.Direction.North, t3, t4, tst, fn = (3))
        subMod.join(2, tam3.Direction.West, t3, t5, tst, west = (1))
        subMod.join(2, tam3.Direction.South, t2, t6, tst, south = (1))
        subMod.join(2, tam3.Direction.North, t7, t1, tst, uppers = (1))


        cpSubMod = subMod.copyModule(tst)
        cpSubMod.renameModule("copiedSubMod")
        rootMod.add(cpSubMod)
        cpSubMod.rotateClockwise90(tst)


        tiles = subMod.createTiles(tst)
        tiles1 = cpSubMod.createTiles(tst)
        tileSystem = tam3.TileSystem("subModRotateNew",tiles)
        tileSystem.writeToFiles("subModRotateNew")
        tileSystem = tam3.TileSystem("cpSubModRotateNew",tiles1)
        tileSystem.writeToFiles("cpSubModRotateNew")

    def test_rotateModuleCounterclockwise(self):
        rootMod = tam3.Module("rootMod")
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")
        t4 = tam3.TileTemplate("t4")
        t5 = tam3.TileTemplate("t5")
        t6 = tam3.TileTemplate("t6")
        t7 = tam3.TileTemplate("t7")
        tst = tam3.TileSetTemplate()
        subMod = tam3.Module("subMod")
        rootMod.add(subMod)
        subMod.add(t1)
        subMod.add(t2)
        subMod.add(t3)
        subMod.add(t4)
        subMod.add(t5)
        subMod.add(t6)
        subMod.add(t7)

        #all wrong joins are getting rotated counter clockwise instead of clockwise

        subMod.join(2, tam3.Direction.North, t1, t3, tst, up = (1))
        subMod.join(2, tam3.Direction.East, t1, t2, tst, east = (1))
        subMod.join(2,tam3.Direction.North, t3, t4, tst, fn = (3))
        subMod.join(2, tam3.Direction.West, t3, t5, tst, west = (1))
        subMod.join(2, tam3.Direction.South, t2, t6, tst, south = (1))
        subMod.join(2, tam3.Direction.North, t7, t1, tst, uppers = (1))


        cpSubMod = subMod.copyModule(tst)
        cpSubMod.renameModule("copiedSubMod")
        rootMod.add(cpSubMod)
        cpSubMod.rotateCounterclockwise90(tst)


        tiles = subMod.createTiles(tst)
        tiles1 = cpSubMod.createTiles(tst)
        tileSystem = tam3.TileSystem("subModCounterRotateNew",tiles)
        tileSystem.writeToFiles("subModCounterRotateNew")
        tileSystem = tam3.TileSystem("cpSubModCounterRotateNew",tiles1)
        tileSystem.writeToFiles("cpSubModCounterRotateNew")

    def test_reflectModuleHorizontal(self):
        rootMod = tam3.Module("rootMod")
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")
        t4 = tam3.TileTemplate("t4")
        t5 = tam3.TileTemplate("t5")
        t6 = tam3.TileTemplate("t6")
        t7 = tam3.TileTemplate("t7")
        tst = tam3.TileSetTemplate()
        subMod = tam3.Module("subMod")
        rootMod.add(subMod)
        subMod.add(t1)
        subMod.add(t2)
        subMod.add(t3)
        subMod.add(t4)
        subMod.add(t5)
        subMod.add(t6)
        subMod.add(t7)

        #all wrong joins are getting rotated counter clockwise instead of clockwise

        subMod.join(2, tam3.Direction.North, t1, t3, tst, up = (1))
        subMod.join(2, tam3.Direction.East, t1, t2, tst, east = (1))
        subMod.join(2,tam3.Direction.North, t3, t4, tst, fn = (3))
        subMod.join(2, tam3.Direction.West, t3, t5, tst, west = (1))
        subMod.join(2, tam3.Direction.South, t2, t6, tst, south = (1))
        subMod.join(2, tam3.Direction.North, t7, t1, tst, uppers = (1))


        cpSubMod = subMod.copyModule(tst)
        cpSubMod.renameModule("copiedSubMod")
        rootMod.add(cpSubMod)
        cpSubMod.reflectModuleHorizontal(tst)

        tiles = subMod.createTiles(tst)
        tiles1 = cpSubMod.createTiles(tst)
        tileSystem = tam3.TileSystem("subModCounterReflectHoriz",tiles)
        tileSystem.writeToFiles("subModCounterReflectHoriz")
        tileSystem = tam3.TileSystem("cpSubModCounterReflectHoriz",tiles1)
        tileSystem.writeToFiles("cpSubModCounterReflectHoriz")

    def test_reflectModuleVertical(self):
        rootMod = tam3.Module("rootMod")
        t1 = tam3.TileTemplate("t1")
        t2 = tam3.TileTemplate("t2")
        t3 = tam3.TileTemplate("t3")
        t4 = tam3.TileTemplate("t4")
        t5 = tam3.TileTemplate("t5")
        t6 = tam3.TileTemplate("t6")
        t7 = tam3.TileTemplate("t7")
        tst = tam3.TileSetTemplate()
        subMod = tam3.Module("subMod")
        rootMod.add(subMod)
        subMod.add(t1)
        subMod.add(t2)
        subMod.add(t3)
        subMod.add(t4)
        subMod.add(t5)
        subMod.add(t6)
        subMod.add(t7)

        #all wrong joins are getting rotated counter clockwise instead of clockwise

        subMod.join(2, tam3.Direction.North, t1, t3, tst, up = (1))
        subMod.join(2, tam3.Direction.East, t1, t2, tst, east = (1))
        subMod.join(2,tam3.Direction.North, t3, t4, tst, fn = (3))
        subMod.join(2, tam3.Direction.West, t3, t5, tst, west = (1))
        subMod.join(2, tam3.Direction.South, t2, t6, tst, south = (1))
        subMod.join(2, tam3.Direction.North, t7, t1, tst, uppers = (1))


        cpSubMod = subMod.copyModule(tst)
        cpSubMod.renameModule("copiedSubMod")
        rootMod.add(cpSubMod)
        cpSubMod.reflectModuleVertical(tst)

        tiles = subMod.createTiles(tst)
        tiles1 = cpSubMod.createTiles(tst)
        tileSystem = tam3.TileSystem("subModCounterReflectVert",tiles)
        tileSystem.writeToFiles("subModCounterReflectVert")
        tileSystem = tam3.TileSystem("cpSubModCounterReflectVert",tiles1)
        tileSystem.writeToFiles("cpSubModCounterReflectVert")
    def test_rotateModule180(self):
        pass






if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()








    
