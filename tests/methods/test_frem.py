from io import StringIO

import numpy as np
import pandas as pd

from pharmpy import Model
from pharmpy.methods.frem.results import FREMResults, bipp_covariance


def test_bipp_covariance(testdata):
    model = Model(testdata / 'nonmem' / 'frem' / 'pheno' / 'model_4.mod')
    cov = bipp_covariance(model, 2)
    cov


def test_frem_results_pheno(testdata):
    model = Model(testdata / 'nonmem' / 'frem' / 'pheno' / 'model_4.mod')
    np.random.seed(39)
    res = FREMResults(model, continuous=['APGR', 'WGT'], samples=10)

    correct = pd.DataFrame({
        'parameter': ['0', '0', '0', '0', '1', '1', '1', '1'],
        'covariate': ['APGR', 'APGR', 'WGT', 'WGT', 'APGR', 'APGR', 'WGT', 'WGT'],
        'condition': ['5th', '95th', '5th', '95th', '5th', '95th', '5th', '95th'],
        '5th': [1.021471, 0.855472, 0.862255, 0.976016, 0.813598, 1.020936, 0.942373, 0.915405],
        'mean': [1.159994, 0.935780, 0.939846, 1.145692, 0.876731, 1.065829, 1.005247, 0.993865],
        '95th': [1.389830, 0.990048, 1.013764, 1.359351, 0.957428, 1.103065, 1.044549, 1.129945]})
    pd.testing.assert_frame_equal(res.covariate_effects, correct)

    correct = """,parameter,observed,5th,95th
1.0,0,0.974787628525673,0.9404264854788376,0.9818769791865711
1.0,1,1.0220100211774878,1.0050370645296267,1.0271736843358379
2.0,0,0.9322193602958176,0.8349257890286346,0.9712071754974831
2.0,1,1.0863060524919126,1.0223184516672452,1.1073589355085347
3.0,0,1.0091536233934566,1.001937649639671,1.0281476002522005
3.0,1,0.9872706597459394,0.9843221847194776,0.9966413138904178
4.0,0,0.9606207522118253,0.8812332453173569,1.0135660814225842
4.0,1,1.003501058808901,0.9708375413213933,1.0322946795457462
5.0,0,0.974787628525673,0.9404264854788376,0.9818769791865711
5.0,1,1.0220100211774878,1.0050370645296267,1.0271736843358379
6.0,0,1.010960869697585,0.9626229536716822,1.0851986449208786
6.0,1,0.9641361715262539,0.9474230023091901,0.9971230579026553
7.0,0,0.9944872959330749,0.9214086942338469,1.0753020252227097
7.0,1,0.9693908394797994,0.9439756489488248,1.0050640341421608
8.0,0,0.9589034965235579,0.897117705873169,0.9722960672474761
8.0,1,1.0275801091641075,1.0004527054778583,1.0399780556788991
9.0,0,0.9493585953571453,0.8869600512954363,0.9717176873867448
9.0,1,1.055100455328332,1.0138175544843107,1.0681986763796631
10.0,0,0.974787628525673,0.9404264854788376,0.9818769791865711
10.0,1,1.0220100211774878,1.0050370645296267,1.0271736843358379
11.0,0,0.9589034965235579,0.897117705873169,0.9722960672474761
11.0,1,1.0275801091641075,1.0004527054778583,1.0399780556788991
12.0,0,0.9927094986473942,0.9612281672946054,1.0182676514876956
12.0,1,0.9926514136793081,0.9817421103084205,1.0058745019041289
13.0,0,0.9765333303674195,0.9202126851359765,1.0150526947170735
13.0,1,0.998061493423796,0.9765066707622273,1.0188963252813406
14.0,0,0.9510587575256984,0.8762015050595144,0.9714177194747982
14.0,1,1.0303765269775598,0.9971765992494146,1.0465940183970204
15.0,0,0.9668129422805504,0.9185795376065111,0.9733914386293293
15.0,1,1.0247912807632464,1.0035220396641717,1.0334056421812001
16.0,0,0.9095267118698269,0.8009620865353312,0.9430032005880522
16.0,1,1.0951989064762164,1.022695756753159,1.1182431972909042
17.0,0,1.0026902520717458,0.9417523018347664,1.080186585405375
17.0,1,0.9667599353969294,0.9456922816314794,1.0007772522942384
18.0,0,0.9944872959330749,0.9214086942338469,1.0753020252227097
18.0,1,0.9693908394797994,0.9439756489488248,1.0050640341421608
19.0,0,1.1053966073550503,1.0036565365982064,1.4131448975917391
19.0,1,0.8533835882796981,0.8216502825580798,0.9641513405624227
20.0,0,0.9845881945267835,0.9404587655289749,1.0158422704711434
20.0,1,0.9953527778561793,0.9793606694516137,1.0122642770020271
21.0,0,1.0073496078169473,0.97471065625839,1.048079472336644
21.0,1,1.0109602609890682,0.994073674619684,1.0248038547749165
22.0,0,0.957189310690998,0.8948653791375218,0.9812998420197734
22.0,1,1.0522369373511546,1.0136260025681645,1.0647201644480657
23.0,0,1.2458831194124333,1.1777642932294263,1.7539708702591352
23.0,1,0.8590846978787242,0.8104918263532488,0.9860870666555259
24.0,0,1.2898065460488006,1.228680525393907,1.8960459562937053
24.0,1,0.8298833659920394,0.7798180680015087,0.9718318448226384
25.0,0,1.078488373466804,0.9438005946287329,1.3941243356817097
25.0,1,0.8603696633602557,0.8186849381599031,0.9742255295613883
26.0,0,1.0986748496525185,0.9239383435215645,1.4659551166117084
26.0,1,1.0288376555754981,0.9288092677631552,1.1364011219518906
27.0,0,1.0707971800371383,1.0528713865146948,1.1813196259664536
27.0,1,0.9459681291986676,0.9326030974491732,0.9876691804464637
28.0,0,1.0719302408624465,0.9188921758226687,1.3679964930701851
28.0,1,1.0372600546071509,0.9466788506205037,1.1261244021360866
29.0,0,0.9432781959243836,0.8558161796778232,0.9705692942981503
29.0,1,1.0331805548571447,0.9939144549590619,1.053253829092999
30.0,0,0.9810711387023736,0.9101140502171128,1.024164358607576
30.0,1,1.0436929282351648,1.0063446770588311,1.0603054368703553
31.0,0,0.9493585953571453,0.8869600512954363,0.9717176873867448
31.0,1,1.055100455328332,1.0138175544843107,1.0681986763796631
32.0,0,1.1077371892512407,0.9256825575547856,1.5003750343229567
32.0,1,1.0260454142230664,0.9227653586948521,1.1398582687765162
33.0,0,0.9730450473914594,0.9055020139336152,1.0037540338019146
33.0,1,1.046533194867676,1.0099432826428314,1.0590941168415835
34.0,0,1.0815630311103914,1.0433530549377346,1.2000733491030267
34.0,1,0.9212942981483625,0.9040793124231854,0.9791220157078377
35.0,0,1.1248964293826664,1.0738575128589374,1.3632809503243906
35.0,1,0.9306682547212441,0.897960671542905,1.0045044334993052
36.0,0,1.03618429556192,1.0124879718764244,1.1018979610346578
36.0,1,0.9563075276665232,0.9464376432326478,0.9879934192361145
37.0,0,0.9095267118698269,0.8009620865353312,0.9430032005880522
37.0,1,1.0951989064762164,1.022695756753159,1.1182431972909042
38.0,0,0.9415919426929809,0.8678543204558119,0.9622351930854139
38.0,1,1.0579717659755008,1.0138277618077383,1.0716909187423422
39.0,0,0.9382284741437185,0.7975775673106207,1.0044172935629325
39.0,1,1.109353060529306,1.0234236362495515,1.1388955190136536
40.0,0,1.0571247398166508,0.9830437890392674,1.2383626298852648
40.0,1,0.907071102862022,0.8823494618627619,0.9802230325173229
41.0,0,0.9991085337343418,0.9697274171522885,1.0251795347895507
41.0,1,1.0137114501735511,0.9996048148783625,1.0229093494974173
42.0,0,1.0372807308673064,0.8985567369131262,1.2488578313862553
42.0,1,1.0485972706172273,0.9709062999594144,1.1170127163086545
43.0,0,1.0963534159335382,0.9832144230515908,1.4066397178735592
43.0,1,0.8557059542409411,0.8206511251510248,0.9673128720869331
44.0,0,0.974787628525673,0.9404264854788376,0.9818769791865711
44.0,1,1.0220100211774878,1.0050370645296267,1.0271736843358379
45.0,0,1.0590178953627924,0.9438281460246993,1.3079239698598064
45.0,1,0.8858159125690391,0.8489177852545279,0.9807963733784358
46.0,0,0.9262487332879905,0.8294291176332554,0.9435786763404528
46.0,1,1.0637378501642383,1.013854438013312,1.0810181426357148
47.0,0,1.0203782758399829,0.8878882406068267,1.1938037281385465
47.0,1,1.0543122625829007,0.9832584592837018,1.112748097846439
48.0,0,0.8963082917194926,0.754755072640469,0.926606484317251
48.0,1,1.0753644675509202,1.0033675012843282,1.1086312886019938
49.0,0,0.9415919426929809,0.8678543204558119,0.9622351930854139
49.0,1,1.0579717659755008,1.0138277618077383,1.0716909187423422
50.0,0,0.9765333303674195,0.9202126851359765,1.0150526947170735
50.0,1,0.998061493423796,0.9765066707622273,1.0188963252813406
51.0,0,0.887386461639495,0.7489371159684193,0.9156704339562873
51.0,1,1.10416456025005,1.022742064354358,1.1309741113950769
52.0,0,0.9355612866877128,0.8359473895136671,0.9697506785500194
52.0,1,1.0359922135126096,0.9906662068673342,1.0599577886308817
53.0,0,0.9730450473914594,0.9055020139336152,1.0037540338019146
53.0,1,1.046533194867676,1.0099432826428314,1.0590941168415835
54.0,0,0.9810711387023736,0.9101140502171128,1.024164358607576
54.0,1,1.0436929282351648,1.0063446770588311,1.0603054368703553
55.0,0,1.0295477996858795,0.9633365891752962,1.1565617675210336
55.0,1,0.936440067918556,0.9138659254547379,0.9904430570705107
56.0,0,0.988117858694446,0.8643836810597042,1.1314877285997145
56.0,1,0.9492515715913541,0.9060442990602352,1.0106258548725133
57.0,0,1.0601384919733423,1.0243575628671684,1.1734574731500553
57.0,1,0.9713027674849692,0.9511755393845582,1.010753734219014
58.0,0,0.9493585953571453,0.8869600512954363,0.9717176873867448
58.0,1,1.055100455328332,1.0138175544843107,1.0681986763796631
59.0,0,0.9765333303674195,0.9202126851359765,1.0150526947170735
59.0,1,0.998061493423796,0.9765066707622273,1.0188963252813406
"""

    correct = pd.read_csv(StringIO(correct), index_col=0)
    correct['parameter'] = correct['parameter'].astype(str)
    pd.testing.assert_frame_equal(res.individual_effects, correct)

    correct = """parameter,condition,sd_observed,sd_5th,sd_95th
0,none,0.19836380718266122,0.17043119968781134,0.2571122896534397
0,APGR,0.1932828383897819,0.16286797347439572,0.25676665494534223
0,WGT,0.19363776172900196,0.1570315937463376,0.24305552931107305
0,all,0.1851006246151042,0.14545696634659333,0.22339242428129563
1,none,0.16105092362355455,0.12034716530602935,0.18097989530487268
1,APGR,0.1468832868065463,0.11595393414184042,0.16855369364464015
1,WGT,0.16104200315990183,0.11955480219369144,0.1776783523537583
1,all,0.14572521381314374,0.11534269901794805,0.16219608849175327
"""
    correct = pd.read_csv(StringIO(correct))
    correct['parameter'] = correct['parameter'].astype(str)
    pd.testing.assert_frame_equal(res.unexplained_variability, correct)

    correct = pd.DataFrame({'5th': [1.0, 0.7], 'ref': [6.423729, 1.525424], '95th': [9.0, 3.2]},
                           index=['APGR', 'WGT'])
    pd.testing.assert_frame_equal(res.covariate_statistics, correct)


def test_frem_results_pheno_categorical(testdata):
    model = Model(testdata / 'nonmem' / 'frem' / 'pheno_cat' / 'model_4.mod')
    np.random.seed(8978)
    res = FREMResults(model, continuous=['WGT'], categorical=['APGRX'], samples=10)
    correct = """parameter,covariate,condition,5th,mean,95th
0,WGT,5th,0.885450,0.943864,0.983854
0,WGT,95th,1.033729,1.130580,1.279973
0,APGRX,other,1.031660,1.106732,1.177195
1,WGT,5th,0.923518,1.012022,1.089995
1,WGT,95th,0.840637,0.986076,1.178471
1,APGRX,other,0.860920,0.924212,0.993316
"""
    correct = pd.read_csv(StringIO(correct))
    correct['parameter'] = correct['parameter'].astype(str)
    pd.testing.assert_frame_equal(res.covariate_effects, correct)

    correct = """,parameter,observed,5th,95th
1.0,0,0.9912884480992122,0.980294735888103,0.9982672055174284
1.0,1,1.0011658066931033,0.9878384918567542,1.0125341721845007
2.0,0,0.9982279801353178,0.9959739263483535,0.9996485147778533
2.0,1,1.0002362024187312,0.9975204359292644,1.0025270061068452
3.0,0,0.9982279801353178,0.9959739263483535,0.9996485147778533
3.0,1,1.0002362024187312,0.9975204359292644,1.0025270061068452
4.0,0,0.957307754163352,0.9055255732527834,0.9913892620235935
4.0,1,1.0058268035357498,0.94108272345739,1.0642265250846712
5.0,0,0.9912884480992122,0.980294735888103,0.9982672055174284
5.0,1,1.0011658066931033,0.9878384918567542,1.0125341721845007
6.0,0,1.1198437615180021,0.992205072689514,1.1662503258181587
6.0,1,0.9085975139522281,0.8613962964465741,1.0241153385690274
7.0,0,1.1043279079656827,0.9636457246078729,1.1617409242208494
7.0,1,0.9102871721081347,0.8635764758820325,1.0383641552807183
8.0,0,0.9775537764268318,0.9496731988085872,0.9955103154805488
8.0,1,1.0030276079249114,0.9688096153133763,1.0328759926241982
9.0,0,0.9912884480992122,0.980294735888103,0.9982672055174284
9.0,1,1.0011658066931033,0.9878384918567542,1.0125341721845007
10.0,0,0.9912884480992122,0.980294735888103,0.9982672055174284
10.0,1,1.0011658066931033,0.9878384918567542,1.0125341721845007
11.0,0,0.9775537764268318,0.9496731988085872,0.9955103154805488
11.0,1,1.0030276079249114,0.9688096153133763,1.0328759926241982
12.0,0,0.9843971586548178,0.9648624565553192,0.9968878066331378
12.0,1,1.0020962749275129,0.9782686935977156,1.02265008206234
13.0,0,0.9707579683714311,0.9347231343974087,0.9941347294188928
13.0,1,1.003959806488996,0.9594598500353174,1.043213175868161
14.0,0,0.9707579683714311,0.9347231343974087,0.9941347294188928
14.0,1,1.003959806488996,0.9594598500353174,1.043213175868161
15.0,0,0.9843971586548178,0.9648624565553192,0.9968878066331378
15.0,1,1.0020962749275129,0.9782686935977156,1.02265008206234
16.0,0,0.9775537764268318,0.9496731988085872,0.9955103154805488
16.0,1,1.0030276079249114,0.9688096153133763,1.0328759926241982
17.0,0,1.1120587747082418,0.9778207666296739,1.1639932754245392
17.0,1,0.9094419506268969,0.8624849044437845,1.0311938027689715
18.0,0,1.1043279079656827,0.9636457246078729,1.1617409242208494
18.0,1,0.9102871721081347,0.8635764758820325,1.0383641552807183
19.0,0,1.1043279079656827,0.9636457246078729,1.1617409242208494
19.0,1,0.9102871721081347,0.8635764758820325,1.0383641552807183
20.0,0,0.9775537764268318,0.9496731988085872,0.9955103154805488
20.0,1,1.0030276079249114,0.9688096153133763,1.0328759926241982
21.0,0,1.0193394208626636,1.0038039313153209,1.0445327999957672
21.0,1,0.9974525653375061,0.9731456247071397,1.027253689896003
22.0,0,0.9982279801353178,0.9959739263483535,0.9996485147778533
22.0,1,1.0002362024187312,0.9975204359292644,1.0025270061068452
23.0,0,1.2785614775943503,1.111742665289813,1.4622409358305468
23.0,1,0.8927013652341582,0.8115540710197318,1.1610521915810612
24.0,0,1.2875120694739488,1.1140419679213438,1.483334464238269
24.0,1,0.8918724725579285,0.804541473729858,1.1709351616730503
25.0,0,1.081456278854311,0.9223458554614994,1.1550119624722557
25.0,1,0.9128275526885249,0.8632749910705567,1.0659199534045485
26.0,0,1.1476873977211168,1.0276799840607147,1.367985626114955
26.0,1,0.9818243185728661,0.8234106025964307,1.2170842496200687
27.0,0,1.1758861925567694,1.0567384456008821,1.2371746939954438
27.0,1,0.9027083706870129,0.8538583415750094,1.0522470426400217
28.0,0,1.1239177543868035,1.0234256400637083,1.3043843449161165
28.0,1,0.9845643411818642,0.8478946725097223,1.180750289569952
29.0,0,0.9640094037600635,0.9200084953960761,0.9927610458110598
29.0,1,1.0048928714242114,0.9502180094117778,1.0536629190926243
30.0,0,1.0193394208626636,1.0038039313153209,1.0445327999957672
30.0,1,0.9974525653375061,0.9731456247071397,1.027253689896003
31.0,0,0.9912884480992122,0.980294735888103,0.9982672055174284
31.0,1,1.0011658066931033,0.9878384918567542,1.0125341721845007
32.0,0,1.15572180332646,1.0291020286268193,1.3898681148206773
32.0,1,0.9809126732918086,0.8154216233480762,1.2294869332711489
33.0,0,1.0122531252393103,1.0024168750231846,1.0280889111768308
33.0,1,0.9983795825420214,0.9828339522876723,1.0172265607681161
34.0,0,1.1595938501918188,1.0419353254684227,1.2098674087490675
34.0,1,0.9043870771962372,0.8559974263431832,1.035754278195865
35.0,0,1.2261495780850629,1.096482370261715,1.344630773279686
35.0,1,0.897690923937966,0.8413284461105773,1.1044616773705846
36.0,0,1.1435272443151587,1.025604395703951,1.1911013700402187
36.0,1,0.9060689054839179,0.8581481724964313,1.0196971851828396
37.0,0,0.9775537764268318,0.9496731988085872,0.9955103154805488
37.0,1,1.0030276079249114,0.9688096153133763,1.0328759926241982
38.0,0,0.9843971586548178,0.9648624565553192,0.9968878066331378
38.0,1,1.0020962749275129,0.9782686935977156,1.02265008206234
39.0,0,1.026475324221878,1.005192908598061,1.0612397908864355
39.0,1,0.9965264088886718,0.963561160892435,1.0373988620926213
40.0,0,1.1120587747082418,0.9778207666296739,1.1639932754245392
40.0,1,0.9094419506268969,0.8624849044437845,1.0311938027689715
41.0,0,1.0122531252393103,1.0024168750231846,1.0280889111768308
41.0,1,0.9983795825420214,0.9828339522876723,1.0172265607681161
42.0,0,1.0929889139324802,1.0177805893080494,1.2241598795214141
42.0,1,0.9882296032263663,0.8817840490398039,1.1342757145638722
43.0,0,1.0966507850556892,0.9496768915812882,1.159493261867576
43.0,1,0.9111331791253289,0.8646710188548223,1.0462793882068084
44.0,0,0.9912884480992122,0.980294735888103,0.9982672055174284
44.0,1,1.0011658066931033,0.9878384918567542,1.0125341721845007
45.0,0,1.0890270323591535,0.9359112572624806,1.157250278048823
45.0,1,0.9119799724085443,0.8646440698963049,1.0560464444573263
46.0,0,0.9707579683714311,0.9347231343974087,0.9941347294188928
46.0,1,1.003959806488996,0.9594598500353174,1.043213175868161
47.0,0,1.0778451443231407,1.0149697614578466,1.1859179449830615
47.0,1,0.9900673478639636,0.8992803899555089,1.1118509137822143
48.0,0,0.9440438976964787,0.8772403366019745,0.9886513833941737
48.0,1,1.007697272512306,0.9231264259686289,1.0857006151100366
49.0,0,0.9843971586548178,0.9648624565553192,0.9968878066331378
49.0,1,1.0020962749275129,0.9782686935977156,1.02265008206234
50.0,0,0.9707579683714311,0.9347231343974087,0.9941347294188928
50.0,1,1.003959806488996,0.9594598500353174,1.043213175868161
51.0,0,0.957307754163352,0.9055255732527834,0.9913892620235935
51.0,1,1.0058268035357498,0.94108272345739,1.0642265250846712
52.0,0,0.957307754163352,0.9055255732527834,0.9913892620235935
52.0,1,1.0058268035357498,0.94108272345739,1.0642265250846712
53.0,0,1.0122531252393103,1.0024168750231846,1.0280889111768308
53.0,1,0.9983795825420214,0.9828339522876723,1.0172265607681161
54.0,0,1.0193394208626636,1.0038039313153209,1.0445327999957672
54.0,1,0.9974525653375061,0.9731456247071397,1.027253689896003
55.0,0,1.1120587747082418,0.9778207666296739,1.1639932754245392
55.0,1,0.9094419506268969,0.8624849044437845,1.0311938027689715
56.0,0,1.073938156098686,0.9089777634376905,1.1528817207315938
56.0,1,0.9136759206966932,0.8612858200050171,1.0759011779953238
57.0,0,1.0408973456983028,1.0079766367903595,1.0954599904578877
57.0,1,0.9946766750618667,0.9446991025087103,1.0580494526368431
58.0,0,0.9912884480992122,0.980294735888103,0.9982672055174284
58.0,1,1.0011658066931033,0.9878384918567542,1.0125341721845007
59.0,0,0.9707579683714311,0.9347231343974087,0.9941347294188928
59.0,1,1.003959806488996,0.9594598500353174,1.043213175868161
"""
    correct = pd.read_csv(StringIO(correct), index_col=0)
    correct['parameter'] = correct['parameter'].astype(str)
    pd.testing.assert_frame_equal(res.individual_effects, correct)

    correct = """parameter,condition,sd_observed,sd_5th,sd_95th
0,none,0.18764141333937986,0.11556469519455893,0.22586836754188136
0,WGT,0.18248555852725476,0.10760209462251279,0.2121611590854133
0,APGRX,0.17859851761700796,0.10158427692847116,0.2206387037336612
0,all,0.17186720148456744,0.09777850745558925,0.20107810018191896
1,none,0.15093077883586237,0.13077925569688323,0.18837661939917977
1,WGT,0.15090452947915595,0.1152285016691207,0.18572399284496208
1,APGRX,0.14429826722004974,0.12314885813466098,0.1797110610103311
1,all,0.1441532460182698,0.10821747330098916,0.17729113916576744
"""

    correct = pd.read_csv(StringIO(correct))
    correct['parameter'] = correct['parameter'].astype(str)
    pd.testing.assert_frame_equal(res.unexplained_variability, correct)

    correct = pd.DataFrame({'5th': [0.7, 0], 'ref': [1.525424, 1], '95th': [3.2, 1]},
                           index=['WGT', 'APGRX'])
    pd.testing.assert_frame_equal(res.covariate_statistics, correct)
