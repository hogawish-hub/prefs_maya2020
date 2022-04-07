# -*- coding: utf-8 -*-
# SkinWeights command and component editor
# Copyright (C) 2018 Trevor van Hoof
# Website: http://www.trevorius.com
#
# pyqt attribute sliders
# Copyright (C) 2018 Daniele Niero
# Website: http://danieleniero.com/
#
# neighbour finding algorythm
# Copyright (C) 2018 Jan Pijpers
# Website: http://www.janpijpers.com/
#
# skinningTools and UI
# Copyright (C) 2018 Perry Leijten
# Website: http://www.perryleijten.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# See http://www.gnu.org/licenses/gpl.html for a copy of the GNU General
# Public License.
#--------------------------------------------------------------------------------------
# unicode converted with
# https://r12a.github.io/app-conversion/

languageDict = {
	"english":{
		"header": u"[EN]",
		"ui"   : u"Skinning_Tools",
		"dock" : u"Skinning_Tools_Dock",
		"extra": u"Extra",
		"hm"   : u"Hold Model",
		"fm"   : u"Fetch Model",
		"so"   : u"Skeleton > Obj",
		"ubt"  : u"Unlock Beta Tab",

		"tools": u"Tools",
		"vbf00": u"Vertex and Bone Functions",
		"vbf01": u"Average",
		"vbf02": u"Copy",
		"vbf03": u"Switch",
		"vbf04": u"Label",
		"vbf05": u"Shell Unify",
		"vbf06": u"copy Skin",
		"vbf07": u"copy Pose",
		"vbf08": u"neighbors",
		"vbf09": u"+ neighbors",
		"vbf10": u"Smooth",
		"vbf11": u"Sm.Brush",
		"vbf12": u"Convert To Joint",
		"vbf13": u"Move",
		"vbf14": u"Swap",
		"vbf15": u"Select",
		"vbf16": u"del.Bone",
		"vbf17": u"Joint infl.",
		"vbf18": u"unify infl.",
		"vbf19": u"sel infl.",
		"vbf20": u"seperate Mesh",
		"vbf21": u"only Selected infl.",
		"vbf22": u"infl. Meshes",
		"vbf23": u"max infl.",
		"vbf24": u"show infl. > max",
		"vbf25": u"Reset Pose",
		"vbf26": u"all joints",
		"vbf27": u"Freeze Joint",
		"vbf28": u"skin:",
		"vbf29": u"Save >>",
		"vbf30": u"<< load",
		"vbf31": u"vertex:",
		"vbf32": u"border Selection",
		"vbf33": u"Store inner",
		"vbf34": u"< Shrink",
		"vbf35": u"Grow >",

		"ctr00": u"Copy/Transfer by Range",
		"ctr01": u"copy skin from source to target",
		"ctr02": u"look for closest amount pts",
		"ctr03": u"Transfer mesh to mesh",
		"ctr04": u"<< Source",
		"ctr05": u"<< Target",
		"ctr06": u"Copy Components",
		"ctr07": u"Reset",

		"mt"   : u"Maya Tools",
		"mt00" : u"Smooth Bind",
		"mt01" : u"Rigid Bind",
		"mt02" : u"Detach Skin",
		"mt03" : u"Paint Skin Weights",
		"mt04" : u"Mirror Skin Weights",
		"mt05" : u"Copy Skin Weights",
		"mt06" : u"Prune Weights",
		"mt07" : u"transfer Skinned UV",
		"mt08" : u"Clean Skinned Mesh",
		"mt09" : u"Combine Skinned Mesh",
		"mt10" : u"Extract Skinned Mesh",
		"mt11" : u"Remove unused infl.",
		"mt12" : u"go to Bindpose",
		"mt13" : u"delete Bindposes",
		"mt14" : u"Weight Hammer",
		"mt15" : u"Create proxy ",
		"mt16" : u"internal",
		"mt17" : u"fast",

		"mvw00": u"Match Vertex Weights",
		"mvw01": u"Store Selection",
		"mvw02": u"Clear list",
		"mvw03": u"No Source",
		"mvw04": u"No Target",
		"mvw05": u"Grab Source",
		"mvw06": u"Grab Target",
		"mvw07": u"Copy Selected vertices",
		"mvw08": u"additive",

		"SEdit": u"Smooth Skin Editor",
		"rload": u"Reload",
		"live" : u"Live",
		"comp" : u"Component Editor",
		"zero" : u"Hide zero columns",

		"wMana": u"Weight Manager",
		"wm001": u"Export Skinweights",
		"wm002": u"name:",
		"wm003": u"prefer",
		"wm004": u"World Positions",
		"wm005": u"UV Positions",
		"wm006": u"Import Skinweights",
		"wm007": u"Delete Skinweights",

		# "bs"   : u"Bind Skin (BETA)",
		# "bs001": u"Visualisation",
		# "bs002": u"Coverage",
		# "bs003": u"Primary Axis",
		# "bs004": u"Skeleton Visualiser",
		# "bs005": u"Transperacy",
		# "bs006": u"Radius",
		# "bs007": u"Segments",
		# "bs008": u"Disc Color",
		# "bs009": u"Visual Color",
		# "bs010": u"Selection Color",
		# "bs011": u"Amount Connected",
		# "bs012": u"Culling Discs",
		# "bs013": u"Auto Scale",
		# "bs014": u"Mask Selections",
		# "bs015": u"Create SkinBind",
		# "bs016": u"Divisions",
		# "bs017": u"Smooth",
		# "bs018": u"Bind Skin",
		# "bs019": u"Surface Detection",
		# "bs020": u"Analyse",
		# "bs021": u"Hard Surface",
		# "bs022": u"Soft Surface",
		# "bs023": u"Add Selection Group",
		# "bs024": u"Clean Scene",

		"smg":   u"Smoothing Graph",
		"average": """The average button needs at least 2 'vertices' as an input,\n
If 2 vertices are selected it will generate a path of edges between the 2 vertices and average the weights over the distance\n
If 3 vertices or more are selected, it will add all the weighting information from every joint on those vertices and combines them. Then it will divide the values by the amount of vertices and apply them on the last selected vertex.\n
If 2 edge loops are selected (i.e. close to an elbow and wrist), it will search vertices on a connecting loop and smooth in between.\n
Makes use of the Smoothing Graph\n
Right click the button to change average function to percentage or distance.""",
		"copy": u"""The copy button is to make sure that multiple vertices have the same value (really useful for solid objects in between stretching skin)\n 
Select all the vertices you want to have the same value, as last select the vertex that has the value you want to apply to all the vertices selected and the use the copy tool.""",
		"boneSwitch": u"""This tool switches the values from one bone to another bone and vice versa. This is especially handy if you have extra joints in for example the shoulder (rolls bone and shoulder bone) if you apply the weights in the wrong order, this tool will switch the weighting values for you while keeping the other values intact. So first select the joints you want the influences switched, then select the mesh to which they are bound and run the tool.""",
		"boneMove": u"""When you want to have all the influence that are on one joint removed and applied to another joint the move tool will do this. Really handy if you want to remove a joint and also be sure where all the weighting values are distributed. Select the bone which has the values, then the bone you want to apply the values to and lastly the mesh which is attached to the bones.""",
		"vertSelect": u"""This is a visualization tool which allows you to select all the vertices that are influenced by a bone or a multiple selection of bones( no matter how small) this makes it easy to see if vertices are influenced that should not be.""",
		"switch": u"This tool only works on 2 vertices not more; it switches the values for both vertices",
		"label": u"""The label will automatically figure out what type a joint is based on naming: it tries to label the joint either 'Left', 'right' or 'center', it will open up a dialogue which presents options as to which naming convention to follow! This will make sure that copying skin, and mirroring skin will have fewer problems with joints that are on top of each other (like roll bones)""",
		"delBone": u"""The delete bone button will remove a bone and try to fix the skinning (note: the bone should not have any children and should be parented to the bone that will take on its influences) this makes sure that the skin will not be broken""",
		"selInf": u"This option will select all the joints that are influencing the current selected mesh.",
		"unify": u"""Select 2 meshes with a skin cluster, this option will make sure that the same bones are influencing both objects; all objects that are added to make sure the influences are unified will be added with 0.0 weight values. """,
		"smooth": u"""The smooth button works similar to the average button, but it will find all the neighboring vertices for you. Select all vertices that need a smoothed influence on the skin and hit this button to smooth these out (weight hammer works similar but is a bit more harsh)""",
		"copySkin": u"""This will transfer skin from first selected object to other objects using Maya's default copy skin method; this will make sure that the meshes that will receive the skin value are detached from their skin cluster before creating a new one""",
		"copyPose": u"""this will do the same as the Transfer skin button except it deletes the history of the skin cluster before copying the skin keeping the pose the mesh is in. (right click options added for non-smooth operation and for skinning based on uv positions which is better for LODs)""",
		"add": u"""Adds a joint to the selected mesh as an influence, it will be added with 0.0 weight value for the joint so it does not break the skin.""",
		"smoothBrush": u"""The smooth brush is an adaptation of the smooth button to a brush, it will allow to smooth over all bones at once (standard smooth brush of Maya allow smoothing only over 1 bone at a time)""",
		"seperate": u"""Separates the skinned meshes by their mesh shells but keeps the skinning information intact, allows the used to focus on the skinned mesh piece by piece, the mesh can later be combined back into one piece if desired.""",
		"neighbors": u"""this option can smooth out the weights, uses a less invasive way of smoothing then the weights hammer, 'neighbors' only smooth's the first detectable components outside of the selection""",
		"neighborsPlus": u"""neighbors + smooth's the selection first. then smooth's the first detectable components outside of the selection, this will give a better falloff. right ckick the button to make the selection grow with each click""",
		"convertToJoint":u"""Convers selection or cluster into a joint. using the selection as influence, also takes in smooth selection operations.""",
		"maxInf": u"""The field that comes with this button allows for input how many joints you want to have as an influence per vertex as a maximum, for example; 8 will allow only 8 bones to influence a certain vertex for every vertex in that selected mesh.""",
		"showMaxInf": u"""This will help visualize and select which vertices have more bone influences then specified in the input above""",
		"resetPose" : u"resets the mesh's bindpose positions allows for the moving of bones without destroying the skincluster",
		"freezeJoint" : u"re-computes joint orientation of skinned or constrained joints, making sure that the rotations are set back to 0",
		"shellUnify" : u"Converts selection into separate clusters, each cluster will be analyzed for its average weight value and this will then be applied to that cluster. Makes for easy hard surface skinning",
		"onlySel" : u"Select components you want to isolate joint influences for, and select the joints. When used this function will remove all the influences of all the joints that are not selected from your selected components",
		"infMesh" : u"Selects all objects that are influenced by current joint selection",
		},
	"japanese":{
		"header": u"[JPN]",
		"ui"   : u"Skinning_Tools",
		"dock" : u"Skinning_Tools_Dock",
		"extra": u"\u4F59\u5206",
		"hm"   : u"\u6301\u3064 \u30E2\u30C7\u30EB",
		"fm"   : u"\u30E2\u30C7\u30EB\u8AAD\u307F\u8FBC\u307F",
		"so"   : u"\u30B9\u30B1\u30EB\u30C8\u30F3 > \u30E2\u30C7\u30EB",
		"ubt"  : u"Beta\u7248\u30BF\u30D6\u3092\u89E3\u9664",

		"tools": u"\u30C4\u30FC\u30EB",
		"vbf00": u"\u9802\u70B9\u3068\u30DC\u30FC\u30F3\u6A5F\u80FD",
		"vbf01": u"\u5E73\u5747",
		"vbf02": u"\u30B3\u30D4\u30FC",
		"vbf03": u"\u5207\u308A\u66FF\u3048",
		"vbf04": u"\u30E9\u30D9\u30EB",
		"vbf05": u"\u30B7\u30A7\u30EB\u7D71\u5408",
		"vbf06": u"Skin\u3092\u30B3\u30D4\u30FC",
		"vbf07": u"Pose\u3092\u30B3\u30D4\u30FC",
		"vbf08": u"\u96A3\u63A5",
		"vbf09": u"\u96A3\u63A5 +",
		"vbf10": u"\u30B9\u30E0\u30FC\u30B7\u30F3\u30B0",
		"vbf11": u"\u30B9\u30E0\u30FC\u30B7\u30F3\u30B0 \u30DA\u30F3",
		"vbf12": u"Joint\u306B\u5909\u63DB",
		"vbf13": u"\u52D5\u304B\u3059",
		"vbf14": u"\u5165\u66FF",
		"vbf15": u"\u9078\u629E",
		"vbf16": u"Bone\u3092\u524A\u9664",
		"vbf17": u"Joint\u306E\u30A4\u30F3\u30D5.",
		"vbf18": u"\u30A4\u30F3\u30D5.\u3092\u7D71\u5408",
		"vbf19": u"\u30A4\u30F3\u30D5.\u3092\u9078\u629E",
		"vbf20": u"\u30E1\u30C3\u30B7\u30E5\u3092\u5206\u5272",
		"vbf21": u"\u9078\u629E\u3055\u308C\u305F\u30A4\u30F3\u30D5.\u306E\u307F",
		"vbf22": u"\u5F71\u97FF\u3055\u308C\u305F\u30E1\u30C3\u30B7\u30E5",
		"vbf23": u"\u6700\u5927\u30A4\u30F3\u30D5.",
		"vbf24": u"\u30A4\u30F3\u30D5.\u3092\u8868\u793A>\u6700\u5927",
		"vbf25": u"Pose\u3092\u30EA\u30BB\u30C3\u30C8",
		"vbf26": u"\u5168\u3066\u306EJoint",
		"vbf27": u" Joint\u3092\u51CD\u7D50",
		"vbf28": u"Skin",
		"vbf29": u"\u4FDD\u5B58 >>",
		"vbf30": u"<< \u8AAD\u8FBC",
		"vbf31": u"\u9802\u70B9",
		"vbf32": u"\u5883\u754C\u306E\u9078\u629E",
		"vbf33": u"Inner\u3092\u683C\u7D0D",
		"vbf34": u"< \u7E2E\u5C0F",
		"vbf35": u"\u5897\u5927 >",
		"ctr00": u"\u6307\u5B9A\u7BC4\u56F2\u3067\u30B3\u30D4\u30FC\uFF0F\u79FB\u52D5",
		"ctr01": u"\u30BD\u30FC\u30B9\u304B\u3089\u30BF\u30FC\u30B2\u30C3\u30C8\u3078\u30B9\u30AD\u30F3\u3092\u30B3\u30D4\u30FC",
		"ctr02": u"\u6700\u3082\u8FD1\u3044pts\u5024\u3092\u63A2\u3059",
		"ctr03": u"\u30E1\u30C3\u30B7\u30E5\u304B\u3089\u30E1\u30C3\u30B7\u30E5\u3078\u79FB\u52D5",
		"ctr04": u"<< \u30BD\u30FC\u30B9",
		"ctr05": u"<< \u30BF\u30FC\u30B2\u30C3\u30C8",
		"ctr06": u"Component\u3092\u30B3\u30D4\u30FC",
		"ctr07": u"\u30EA\u30BB\u30C3\u30C8",

		"mt"   : u"Maya \u30C4\u30FC\u30EB",
		"mt00" : u"\u30B9\u30E0\u30FC\u30B7\u30F3\u30B0 \u30D0\u30A4\u30F3\u30C9",
		"mt01" : u"\u30EA\u30B8\u30C3\u30C9 \u30D0\u30A4\u30F3\u30C9",
		"mt02" : u"Skin\u3092\u5207\u308A\u96E2\u3059",
		"mt03" : u"\u30B9\u30AD\u30F3\u306E\u30A6\u30A7\u30A4\u30C8\u3092\u30DA\u30A4\u30F3\u30C8",
		"mt04" : u"\u30B9\u30AD\u30F3\u306E\u30A6\u30A7\u30A4\u30C8\u3092\u30DF\u30E9\u30FC",
		"mt05" : u"\u30B9\u30AD\u30F3\u306E\u30A6\u30A7\u30A4\u30C8\u3092\u30B3\u30D4\u30FC",
		"mt06" : u"\u30A6\u30A7\u30A4\u30C8\u306E\u524A\u6E1B",
		"mt07" : u"\u30B9\u30AD\u30F3\u30C9UV\u3092\u79FB\u52D5",
		"mt08" : u"Skinned Mesh \u3092\u30AF\u30EA\u30FC\u30CB\u30F3\u30B0",
		"mt09" : u"Skinned Mesh \u3092\u7D44\u307F\u5408\u308F\u305B\u308B",
		"mt10" : u"Skinned Mesh \u3092\u629C\u304D\u51FA\u3059",
		"mt11" : u"\u672A\u4F7F\u7528\u306E\u30A4\u30F3\u30D5.\u3092\u9664\u53BB",
		"mt12" : u"Bindpose\u3078",
		"mt13" : u"Bindpose\u3092\u524A\u9664",
		"mt14" : u"\u30A6\u30A7\u30A4\u30C8\u30CF\u30F3\u30DE\u30FC",
		"mt15" : u"\u30D7\u30ED\u30AD\u30B7\u30FC\u3092\u4F5C\u6210",
		"mt16" : u"\u5185\u90E8",
		"mt17" : u"\u9AD8\u901F",

		"mvw00": u"\u30DD\u30A4\u30F3\u30C8\u30A6\u30A7\u30A4\u30C8\u3092\u7167\u5408",
		"mvw01": u"\u30BB\u30EC\u30AF\u30B7\u30E7\u30F3\u3092\u4FDD\u5B58",
		"mvw02": u"\u30EA\u30B9\u30C8\u3092\u30AF\u30EA\u30A2",
		"mvw03": u"\u30BD\u30FC\u30B9\u306A\u3057",
		"mvw04": u"\u30BF\u30FC\u30B2\u30C3\u30C8\u306A\u3057",
		"mvw05": u"\u30BD\u30FC\u30B9\u3092\u30B0\u30E9\u30D6",
		"mvw06": u"\u30BF\u30FC\u30B2\u30C3\u30C8\u3092\u30B0\u30E9\u30D6",
		"mvw07": u"\u9078\u629E\u3055\u308C\u305F\u70B9\u3092\u30B3\u30D4\u30FC",
		"mvw08": u"\u8FFD\u52A0",

		"SEdit": u"\u30B9\u30E0\u30FC\u30B9\u30B9\u30AD\u30F3\u30A8\u30C7\u30A3\u30BF\u30FC",
		"rload": u"\u88DC\u5145\u3059\u308B",
		"live" : u"\u516C\u958B",
		"comp" : u"\u30B3\u30F3\u30DD\u30FC\u30CD\u30F3\u30C8\u30A8\u30C7\u30A3\u30BF\u30FC",
		"zero" : u"\u30BC\u30ED\u30B3\u30E9\u30E0\u975E\u8868\u793A",
		
		"wMana": u"\u30A6\u30A7\u30A4\u30C8\u30DE\u30CD\u30FC\u30B8\u30E3",
		"wm001": u"Skinweight\u66F8\u51FA\u3057",
		"wm002": u"\u540D\u79F0",
		"wm003": u"\u512A\u5148",
		"wm004": u"\u30EF\u30FC\u30EB\u30C9\u306E\u4F4D\u7F6E",
		"wm005": u"UV\u4F4D\u7F6E",
		"wm006": u"Skinweight\u3092\u30A4\u30F3\u30DD\u30FC\u30C8",
		"wm007": u"Skinweight\u3092\u524A\u9664",

		# "bs"   : u"\u30D0\u30A4\u30F3\u30C9\u30B9\u30AD\u30F3\uFF08BETA\uFF09",
		# "bs001": u"\u53EF\u8996\u5316",
		# "bs002": u"\u63A9\u8B77",
		# "bs003": u"\u4E3B\u8EF8",
		# "bs004": u"\u30B9\u30B1\u30EB\u30C8\u30F3 \u53EF\u8996\u5316",
		# "bs005": u"\u900F\u904E\u6027",
		# "bs006": u"\u534A\u5F84",
		# "bs007": u"\u30BB\u30B0\u30E1\u30F3\u30C8",
		# "bs008": u"\u30C7\u30A3\u30B9\u30AF\u30AB\u30E9\u30FC",
		# "bs009": u"\u30D3\u30B8\u30E5\u30A2\u30EB\u30AB\u30E9\u30FC",
		# "bs010": u"\u30BB\u30EC\u30AF\u30B7\u30E7\u30F3\u30AB\u30E9\u30FC",
		# "bs011": u"\u63A5\u7D9A\u91D1\u984D",
		# "bs012": u"\u30C7\u30A3\u30B9\u30AF\u306E\u30AB\u30EA\u30F3\u30B0",
		# "bs013": u"\u81EA\u52D5\u30B9\u30B1\u30FC\u30EA\u30F3\u30B0",
		# "bs014": u"\u9078\u629E\u90E8\u5206\u3092\u30DE\u30B9\u30AF",
		# "bs015": u"SkinBind\u3092\u4F5C\u6210",
		# "bs016": u"\u5206\u5272",
		# "bs017": u"\u5E73\u6ED1",
		# "bs018": u"\u30B9\u30AD\u30F3\u3092\u30D0\u30A4\u30F3\u30C9",
		# "bs019": u"\u8868\u9762\u691C\u51FA",
		# "bs020": u"\u5206\u6790",
		# "bs021": u"\u786C\u8868\u9762",
		# "bs022": u"\u67D4\u8868\u9762",
		# "bs023": u"\u9078\u629E\u30B0\u30EB\u30FC\u30D7\u3092\u8FFD\u52A0",
		# "bs024": u"\u6383\u9664",

		"smg":   u"\u30B9\u30E0\u30FC\u30B8\u30F3\u30B0\u30B0\u30E9\u30D5",
		"average": u"""\u5E73\u5747\u7684\u306A\u30DC\u30BF\u30F3\u306F\u5C11\u306A\u304F\u3068\u30822\u3064\u306E '\u9802\u70B9'\u3092\u5165\u529B\u3068\u3057\u3066\u5FC5\u8981\u3068\u3057\u307E\u3059\u3002\n
2\u3064\u306E\u9802\u70B9\u304C\u9078\u629E\u3055\u308C\u3066\u3044\u308B\u5834\u5408\u30012\u3064\u306E\u9802\u70B9\u306E\u9593\u306B\u30A8\u30C3\u30B8\u306E\u30D1\u30B9\u304C\u751F\u6210\u3055\u308C\u3001\u8DDD\u96E2\u306B\u6CBF\u3063\u3066\u30A6\u30A7\u30A4\u30C8\u304C\u5E73\u5747\u5316\u3055\u308C\u307E\u3059\u3002\n
3\u3064\u4EE5\u4E0A\u306E\u9802\u70B9\u304C\u9078\u629E\u3055\u308C\u3066\u3044\u308B\u5834\u5408\u3001\u305D\u308C\u3089\u306E\u9802\u70B9\u306E\u3059\u3079\u3066\u306E\u30B8\u30E7\u30A4\u30F3\u30C8\u304B\u3089\u3059\u3079\u3066\u306E\u30A6\u30A7\u30A4\u30C6\u30A3\u30F3\u30B0\u60C5\u5831\u304C\u8FFD\u52A0\u3055\u308C\u3001\u7D50\u5408\u3055\u308C\u307E\u3059\u3002 \u6B21\u306B\u3001\u5024\u3092\u9802\u70B9\u306E\u6570\u3067\u9664\u7B97\u3057\u3001\u6700\u5F8C\u306B\u9078\u629E\u3057\u305F\u9802\u70B9\u306B\u9069\u7528\u3057\u307E\u3059\u3002\n
2\u3064\u306E\u30A8\u30C3\u30B8\u30EB\u30FC\u30D7\u304C\u9078\u629E\u3055\u308C\u3066\u3044\u308B\u5834\u5408\uFF08\u3064\u307E\u308A\u3001\u8098\u3068\u624B\u9996\u306B\u8FD1\u3044\u5834\u5408\uFF09\u3001\u63A5\u7D9A\u30EB\u30FC\u30D7\u4E0A\u306E\u9802\u70B9\u3092\u691C\u7D22\u3057\u3001\u305D\u306E\u9593\u3067\u6ED1\u3089\u304B\u306B\u306A\u308A\u307E\u3059\u3002\n
\u30B9\u30E0\u30FC\u30B8\u30F3\u30B0\u30B0\u30E9\u30D5\u3092\u4F7F\u7528\u3059\u308B\u307E\u3059\n
\u30DC\u30BF\u30F3\u3092\u53F3\u30AF\u30EA\u30C3\u30AF\u3059\u308B\u3068\u3001\u5E73\u5747\u95A2\u6570\u304C\u30D1\u30FC\u30BB\u30F3\u30C6\u30FC\u30B8\u307E\u305F\u306F\u8DDD\u96E2\u306B\u5909\u66F4\u3055\u308C\u307E\u3059\u3002""",
		"copy": u"""\u30B3\u30D4\u30FC\u30DC\u30BF\u30F3\u306F\u3001\u8907\u6570\u306E\u9802\u70B9\u304C\u540C\u3058\u5024\u3092\u6301\u3064\u3053\u3068\u3092\u78BA\u8A8D\u3059\u308B\u3053\u3068\u3067\u3059\uFF08\u30B9\u30C8\u30EC\u30C3\u30C1\u808C\u306E\u9593\u306E\u30BD\u30EA\u30C3\u30C9\u30AA\u30D6\u30B8\u30A7\u30AF\u30C8\u306B\u306F\u672C\u5F53\u306B\u4FBF\u5229\u3067\u3059\uFF09\u3002\n
\u9078\u629E\u3057\u305F\u3059\u3079\u3066\u306E\u9802\u70B9\u306B\u9069\u7528\u3059\u308B\u5024\u3092\u6301\u3064\u9802\u70B9\u3092\u6700\u5F8C\u306B\u9078\u629E\u3057\u3001\u30B3\u30D4\u30FC\u30C4\u30FC\u30EB\u3092\u4F7F\u7528\u3057\u3066\u3001\u540C\u3058\u5024\u3092\u6301\u3064\u3059\u3079\u3066\u306E\u9802\u70B9\u3092\u9078\u629E\u3057\u307E\u3059\u3002""",
		"boneSwitch": u"""\u3053\u306E\u30C4\u30FC\u30EB\u306F\u3001\u5024\u30921\u3064\u306E\u30DC\u30FC\u30F3\u304B\u3089\u5225\u306E\u30DC\u30FC\u30F3\u306B\u3001\u307E\u305F\u306F\u305D\u306E\u9006\u306B\u5207\u308A\u66FF\u3048\u307E\u3059\u3002 \u3053\u308C\u306F\u3001\u4F53\u91CD\u3092\u9593\u9055\u3063\u305F\u9806\u756A\u3067\u9069\u7528\u3059\u308B\u3068\u3001\u4F8B\u3048\u3070\u3001\u80A9\uFF08\u30ED\u30FC\u30EB\u30DC\u30FC\u30F3\u3068\u80A9\u306E\u9AA8\uFF09\u306B\u4F59\u5206\u306A\u95A2\u7BC0\u304C\u3042\u308B\u5834\u5408\u306B\u7279\u306B\u4FBF\u5229\u3067\u3059\u3002\u3053\u306E\u30C4\u30FC\u30EB\u306F\u4ED6\u306E\u5024\u3092\u305D\u306E\u307E\u307E\u7DAD\u6301\u3057\u306A\u304C\u3089\u4F53\u91CD\u5024\u3092\u5207\u308A\u66FF\u3048\u307E\u3059\u3002 \u305D\u306E\u305F\u3081\u3001\u307E\u305A\u3001\u5F71\u97FF\u3092\u5207\u308A\u66FF\u3048\u305F\u3044\u30B8\u30E7\u30A4\u30F3\u30C8\u3092\u9078\u629E\u3057\u3001\u30D0\u30A4\u30F3\u30C9\u5148\u306E\u30E1\u30C3\u30B7\u30E5\u3092\u9078\u629E\u3057\u3066\u30C4\u30FC\u30EB\u3092\u5B9F\u884C\u3057\u307E\u3059\u3002""",
		"boneMove": u"""\u3053\u306E\u30C4\u30FC\u30EB\u306F\u3001\u30B8\u30E7\u30A4\u30F3\u30C8\u304B\u3089\u3059\u3079\u3066\u306E\u5F71\u97FF\u3092\u9664\u53BB\u3057\u3001\u5225\u306E\u30B8\u30E7\u30A4\u30F3\u30C8\u306B\u9069\u7528\u3057\u307E\u3059\u3002 \u30B8\u30E7\u30A4\u30F3\u30C8\u3092\u524A\u9664\u3057\u3001\u3059\u3079\u3066\u306E\u91CD\u307F\u4ED8\u3051\u5024\u304C\u3069\u3053\u306B\u914D\u5206\u3055\u308C\u3066\u3044\u308B\u304B\u3092\u78BA\u8A8D\u3057\u305F\u3044\u5834\u5408\u306F\u3001\u672C\u5F53\u306B\u4FBF\u5229\u3067\u3059\u3002 \u5024\u3092\u6301\u3064\u30DC\u30FC\u30F3\u3092\u9078\u629E\u3057\u3001\u5024\u3092\u9069\u7528\u3059\u308B\u30DC\u30FC\u30F3\u3092\u9078\u629E\u3057\u3001\u6700\u5F8C\u306B\u30DC\u30FC\u30F3\u306B\u63A5\u7D9A\u3055\u308C\u3066\u3044\u308B\u30E1\u30C3\u30B7\u30E5\u3092\u9078\u629E\u3057\u307E\u3059\u3002""",
		"vertSelect": u"""\u3053\u308C\u306F\u8996\u899A\u5316\u30C4\u30FC\u30EB\u3067\u3042\u308A\u3001\u9AA8\u3084\u8907\u6570\u306E\u9AA8\u306E\u9078\u629E\u306E\u5F71\u97FF\u3092\u53D7\u3051\u3001\u3069\u306E\u3088\u3046\u306B\u5C0F\u3055\u306A\u3082\u306E\u3067\u3042\u3063\u3066\u3082\u3001\u9802\u70B9\u304C\u5F71\u97FF\u3092\u53D7\u3051\u3066\u306F\u3044\u3051\u306A\u3044\u304B\u3069\u3046\u304B\u3092\u78BA\u8A8D\u3059\u308B\u306E\u304C\u5BB9\u6613\u306B\u306A\u308A\u307E\u3059\u3002""",
		"switch": u"""\u3053\u306E\u30C4\u30FC\u30EB\u306F\u3001\u6B63\u78BA\u306B2\u3064\u306E\u9802\u70B9\u3067\u306E\u307F\u6A5F\u80FD\u3057\u307E\u3059\u3002 \u4E21\u65B9\u306E\u9802\u70B9\u306E\u5024\u3092\u5207\u308A\u66FF\u3048\u308B""",
		"label": u"""\u30E9\u30D9\u30EB\u306F\u81EA\u52D5\u7684\u306B\u30B8\u30E7\u30A4\u30F3\u30C8\u304C\u3069\u306E\u30BF\u30A4\u30D7\u306E\u540D\u524D\u4ED8\u3051\u306B\u57FA\u3065\u3044\u3066\u3044\u308B\u304B\u3092\u628A\u63E1\u3057\u307E\u3059\uFF1A\u30B8\u30E7\u30A4\u30F3\u30C8\u306B "Left"\u3001 "Right"\u3001 "Center"\u306E\u3044\u305A\u308C\u304B\u306E\u30E9\u30D9\u30EB\u3092\u4ED8\u3051\u308B\u3068\u3001\u3069\u306E\u547D\u540D\u898F\u5247\u306B\u5F93\u3046\u304B\u3092\u793A\u3059\u30C0\u30A4\u30A2\u30ED\u30B0\u304C\u958B\u304D\u307E\u3059 \uFF01 \u3053\u308C\u306B\u3088\u308A\u3001\u30B9\u30AD\u30F3\u3092\u30B3\u30D4\u30FC\u3057\u305F\u308A\u3001\u30B9\u30AD\u30F3\u3092\u30DF\u30E9\u30FC\u30EA\u30F3\u30B0\u3059\u308B\u3053\u3068\u3067\u3001\u30ED\u30FC\u30EB\u30DC\u30FC\u30F3\u306E\u3088\u3046\u306B\u4E0A\u306B\u3042\u308B\u30B8\u30E7\u30A4\u30F3\u30C8\u306E\u554F\u984C\u304C\u5C11\u306A\u304F\u306A\u308A\u307E\u3059\u3002""",
		"delBone": u"""\u524A\u9664\u30DC\u30FC\u30F3\u30DC\u30BF\u30F3\u306F\u30DC\u30FC\u30F3\u3092\u524A\u9664\u3057\u3001\u30B9\u30AD\u30CB\u30F3\u30B0\u3092\u4FEE\u6B63\u3057\u3088\u3046\u3068\u3057\u307E\u3059\uFF08\u6CE8\u610F\uFF1A\u30DC\u30FC\u30F3\u306B\u306F\u5B50\u304C\u306A\u304F\u3001\u5F71\u97FF\u3092\u53D7\u3051\u308B\u30DC\u30FC\u30F3\u3092\u89AA\u306B\u3059\u308B\u5FC5\u8981\u304C\u3042\u308A\u307E\u3059\uFF09\u3002\u3053\u308C\u306B\u3088\u308A\u3001\u30B9\u30AD\u30F3\u304C\u58CA\u308C\u306A\u3044\u3088\u3046\u306B\u306A\u308A\u307E\u3059""",
		"selInf": u"\u3053\u306E\u30AA\u30D7\u30B7\u30E7\u30F3\u306F\u3001\u73FE\u5728\u9078\u629E\u3055\u308C\u3066\u3044\u308B\u30E1\u30C3\u30B7\u30E5\u306B\u5F71\u97FF\u3092\u4E0E\u3048\u308B\u3059\u3079\u3066\u306E\u30B8\u30E7\u30A4\u30F3\u30C8\u3092\u9078\u629E\u3057\u307E\u3059\u3002",
		"unify": u"""\u30B9\u30AD\u30F3\u30AF\u30E9\u30B9\u30BF\u30672\u3064\u306E\u30E1\u30C3\u30B7\u30E5\u3092\u9078\u629E\u3059\u308B\u3068\u3001\u3053\u306E\u30AA\u30D7\u30B7\u30E7\u30F3\u306F\u540C\u3058\u30DC\u30FC\u30F3\u304C\u4E21\u65B9\u306E\u30AA\u30D6\u30B8\u30A7\u30AF\u30C8\u306B\u5F71\u97FF\u3092\u4E0E\u3048\u308B\u3053\u3068\u3092\u4FDD\u8A3C\u3057\u307E\u3059\u3002 \u5F71\u97FF\u304C\u7D71\u4E00\u3055\u308C\u3066\u3044\u308B\u3053\u3068\u3092\u78BA\u8A8D\u3059\u308B\u305F\u3081\u306B\u8FFD\u52A0\u3055\u308C\u305F\u3059\u3079\u3066\u306E\u30AA\u30D6\u30B8\u30A7\u30AF\u30C8\u306B\u52A0\u91CD\u50240.0\u304C\u8FFD\u52A0\u3055\u308C\u307E\u3059\u3002""",
		"smooth": u"""\u30B9\u30E0\u30FC\u30BA\u30DC\u30BF\u30F3\u306F\u5E73\u5747\u30DC\u30BF\u30F3\u3068\u4F3C\u3066\u3044\u307E\u3059\u304C\u3001\u96A3\u63A5\u3059\u308B\u3059\u3079\u3066\u306E\u9802\u70B9\u3092\u898B\u3064\u3051\u308B\u3053\u3068\u304C\u3067\u304D\u307E\u3059\u3002 \u30B9\u30AD\u30F3\u306B\u30B9\u30E0\u30FC\u30B8\u30F3\u30B0\u3055\u308C\u305F\u5F71\u97FF\u3092\u5FC5\u8981\u3068\u3059\u308B\u3059\u3079\u3066\u306E\u9802\u70B9\u3092\u9078\u629E\u3057\u3001\u3053\u306E\u30DC\u30BF\u30F3\u3092\u62BC\u3057\u3066\u3053\u308C\u3089\u3092\u6ED1\u3089\u304B\u306B\u3057\u307E\u3059\uFF08\u30A6\u30A7\u30A4\u30C8\u30CF\u30F3\u30DE\u30FC\u306F\u540C\u69D8\u306B\u6A5F\u80FD\u3057\u307E\u3059\u304C\u3001\u3082\u3046\u5C11\u3057\u53B3\u3057\u3044\u3067\u3059\uFF09""",
		"copySkin": u"""Maya\u306E\u30C7\u30D5\u30A9\u30EB\u30C8\u306E\u30B3\u30D4\u30FC\u30B9\u30AD\u30F3\u30E1\u30BD\u30C3\u30C9\u3092\u4F7F\u7528\u3057\u3066\u3001\u6700\u521D\u306B\u9078\u629E\u3057\u305F\u30AA\u30D6\u30B8\u30A7\u30AF\u30C8\u304B\u3089\u4ED6\u306E\u30AA\u30D6\u30B8\u30A7\u30AF\u30C8\u306B\u30B9\u30AD\u30F3\u3092\u8EE2\u9001\u3057\u307E\u3059\u3002 \u3053\u308C\u306F\u3001\u65B0\u3057\u3044\u5024\u3092\u4F5C\u6210\u3059\u308B\u524D\u306B\u3001\u30B9\u30AD\u30F3\u5024\u3092\u53D7\u3051\u53D6\u308B\u30E1\u30C3\u30B7\u30E5\u304C\u30B9\u30AD\u30F3\u30AF\u30E9\u30B9\u30BF\u30FC\u304B\u3089\u5207\u308A\u96E2\u3055\u308C\u3066\u3044\u308B\u3053\u3068\u3092\u78BA\u8A8D\u3057\u307E\u3059""",
		"copyPose": u"""\u30E1\u30C3\u30B7\u30E5\u304C\u3042\u308B\u30DD\u30FC\u30BA\u3092\u7DAD\u6301\u3057\u306A\u304C\u3089\u30B9\u30AD\u30F3\u3092\u30B3\u30D4\u30FC\u3059\u308B\u524D\u306B\u3001\u30B9\u30AD\u30F3\u30AF\u30E9\u30B9\u30BF\u30FC\u306E\u30D2\u30B9\u30C8\u30EA\u30FC\u3092\u524A\u9664\u3059\u308B\u70B9\u3092\u9664\u3044\u3066\u3001\u30C8\u30E9\u30F3\u30B9\u30D5\u30A1\u30FC\u30B9\u30AD\u30F3\u30DC\u30BF\u30F3\u3068\u540C\u3058\u3053\u3068\u3092\u884C\u3044\u307E\u3059\uFF08\u53F3\u30AF\u30EA\u30C3\u30AF\u306E\u30AA\u30D7\u30B7\u30E7\u30F3\u306F\u30B9\u30E0\u30FC\u30BA\u3067\u306A\u3044\u64CD\u4F5C\u3068uv\u306E\u4F4D\u7F6E\u306B\u57FA\u3065\u304F\u30B9\u30AD\u30CB\u30F3\u30B0\u3067\u3059\uFF09\u3002 LOD\u306E\u65B9\u304C\u826F\u3044\uFF09""",
		"add": u"""\u9078\u629E\u3057\u305F\u30E1\u30C3\u30B7\u30E5\u306B\u30B8\u30E7\u30A4\u30F3\u30C8\u3092\u5F71\u97FF\u529B\u3068\u3057\u3066\u8FFD\u52A0\u3057\u307E\u3059\u3002\u30B8\u30E7\u30A4\u30F3\u30C8\u306B\u306F0.0\u306E\u30A6\u30A7\u30A4\u30C8\u5024\u304C\u8FFD\u52A0\u3055\u308C\u308B\u305F\u3081\u3001\u30B9\u30AD\u30F3\u304C\u7834\u3089\u308C\u308B\u3053\u3068\u306F\u3042\u308A\u307E\u305B\u3093\u3002""",
		"smoothBrush": u"""\u540C\u6642\u306B\u3059\u3079\u3066\u306E\u30DC\u30FC\u30F3\u3092\u30B9\u30E0\u30FC\u30B8\u30F3\u30B0\u3059\u308B\u3053\u3068\u304C\u3067\u304D\u307E\u3059\uFF08Maya\u306E\u6A19\u6E96\u306E\u30B9\u30E0\u30FC\u30B9\u30D6\u30E9\u30B7\u306F\u3001\u4E00\u5EA6\u306B1\u3064\u306E\u30DC\u30FC\u30F3\u306E\u307F\u3092\u30B9\u30E0\u30FC\u30BA\u306B\u3057\u307E\u3059\uFF09""",
		"seperate": u"""\u30B9\u30AD\u30CB\u30F3\u30B0\u3055\u308C\u305F\u30E1\u30C3\u30B7\u30E5\u3092\u30E1\u30C3\u30B7\u30E5\u30B7\u30A7\u30EB\u3067\u533A\u5207\u308A\u307E\u3059\u304C\u3001\u30B9\u30AD\u30CB\u30F3\u30B0\u60C5\u5831\u306F\u305D\u306E\u307E\u307E\u6B8B\u3057\u3001\u30B9\u30AD\u30F3\u30E1\u30C3\u30B7\u30E5\u306E\u30D4\u30FC\u30B9\u5358\u4F4D\u3067\u30D4\u30F3\u30C8\u3092\u5408\u308F\u305B\u308B\u3053\u3068\u304C\u3067\u304D\u307E\u3059\u3002\u5F8C\u3067\u30E1\u30C3\u30B7\u30E5\u3092\u5FC5\u8981\u306B\u5FDC\u3058\u30661\u3064\u306B\u623B\u3059\u3053\u3068\u304C\u3067\u304D\u307E\u3059\u3002""",
		"neighbors": u"""\u3053\u306E\u30AA\u30D7\u30B7\u30E7\u30F3\u306F\u30A6\u30A7\u30A4\u30C8\u3092\u30B9\u30E0\u30FC\u30BA\u306B\u3057\u307E\u3059\u3002 \u30A6\u30A7\u30A4\u30C8\u30CF\u30F3\u30DE\u30FC\u3088\u308A\u5E73\u6ED1\u5316\u306E\u4FB5\u8972\u6027\u306E\u4F4E\u3044\u65B9\u6CD5\u3092\u4F7F\u7528\u3057\u307E\u3059\u3002\u300C\u96A3\u4EBA\u300D\u306F\u9078\u629E\u7BC4\u56F2\u5916\u306E\u6700\u521D\u306E\u691C\u51FA\u53EF\u80FD\u306A\u6210\u5206\u3060\u3051\u3067\u3059""",
		"neighborsPlus": u"""Neighbor + "\u306F\u9078\u629E\u7BC4\u56F2\u3092\u6ED1\u3089\u304B\u306B\u3057\u3001\u6700\u521D\u306B\u691C\u51FA\u53EF\u80FD\u306A\u30B3\u30F3\u30DD\u30FC\u30CD\u30F3\u30C8\u3092\u9078\u629E\u7BC4\u56F2\u5916\u306B\u6ED1\u3089\u304B\u306B\u3057\u307E\u3059\u3002\u3053\u308C\u306B\u3088\u308A\u3001\u3088\u308A\u826F\u3044\u30D5\u30A9\u30FC\u30EB\u30AA\u30D5\u304C\u5F97\u3089\u308C\u307E\u3059\u3002\u30DC\u30BF\u30F3\u3092\u30AF\u30EA\u30C3\u30AF\u3059\u308B\u3068\u3001\u30AF\u30EA\u30C3\u30AF\u3054\u3068\u306E\u9078\u629E\u7BC4\u56F2\u304C\u62E1\u5927\u3055\u308C\u307E\u3059\u3002""",
		"convertToJoint":u"""\u9078\u629E\u307E\u305F\u306F\u30AF\u30E9\u30B9\u30BF\u3092\u30B8\u30E7\u30A4\u30F3\u30C8\u306B\u5909\u63DB\u3057\u307E\u3059\u3002 \u9078\u629E\u60C5\u5831\u306E\u30C7\u30FC\u30BF\u3092\u5909\u63DB\u3059\u308B\u306E\u3067\u3001\u5186\u6ED1\u306A\u9078\u629E\u64CD\u4F5C\u3082\u53EF\u80FD""",
		"maxInf": u"""\u3053\u306E\u30DC\u30BF\u30F3\u304C\u4ED8\u3044\u3066\u3044\u308B\u30D5\u30A3\u30FC\u30EB\u30C9\u3067\u306F\u3001\u9802\u70B9\u3054\u3068\u306E\u5F71\u97FF\u3068\u3057\u3066\u6700\u5927\u3044\u304F\u3064\u306E\u30B8\u30E7\u30A4\u30F3\u30C8\u3092\u5165\u529B\u3059\u308B\u304B\u3092\u5165\u529B\u3059\u308B\u3053\u3068\u304C\u3067\u304D\u307E\u3059\u3002 8\u306F\u3001\u9078\u629E\u3055\u308C\u305F\u30E1\u30C3\u30B7\u30E5\u5185\u306E\u5404\u9802\u70B9\u306E\u7279\u5B9A\u306E\u9802\u70B9\u306B8\u3064\u306E\u30DC\u30FC\u30F3\u3057\u304B\u5F71\u97FF\u3092\u4E0E\u3048\u306A\u3044\u3088\u3046\u306B\u3057\u307E\u3059\u3002""",
		"showMaxInf": u"""\u3053\u308C\u306F\u3001\u4E0A\u306E\u5165\u529B\u3067\u6307\u5B9A\u3055\u308C\u305F\u30DC\u30FC\u30F3\u306E\u5F71\u97FF\u304C\u3088\u308A\u591A\u3044\u9802\u70B9\u3092\u8996\u899A\u5316\u3057\u3066\u9078\u629E\u3059\u308B\u306E\u306B\u5F79\u7ACB\u3061\u307E\u3059""",
		"resetPose" : u"\u30E1\u30C3\u30B7\u30E5\u306E\u30D0\u30A4\u30F3\u30C9\u4F4D\u7F6E\u3092\u30EA\u30BB\u30C3\u30C8\u3059\u308B\u3068\u3001\u30B9\u30AD\u30F3\u30AF\u30E9\u30B9\u30BF\u30FC\u3092\u7834\u58CA\u3059\u308B\u3053\u3068\u306A\u304F\u9AA8\u304C\u52D5\u304F",
		"freezeJoint" : u"\u30B8\u30E7\u30A4\u30F3\u30C8\u306E\u5411\u304D\u3092\u518D\u8A08\u7B97\u3057\u307E\u3059\u3002 \u30ED\u30FC\u30C6\u30FC\u30B7\u30E7\u30F3\u304C0\u306B\u8A2D\u5B9A\u3055\u308C\u3066\u3044\u308B\u3053\u3068\u3092\u78BA\u8A8D\u3059\u308B",
		"shellUnify" : u"\u9078\u629E\u3092\u5225\u3005\u306E\u30AF\u30E9\u30B9\u30BF\u306B\u5909\u63DB\u3059\u308B\u3068\u3001\u5404\u30AF\u30E9\u30B9\u30BF\u306F\u305D\u306E\u5E73\u5747\u91CD\u307F\u5024\u3092\u5206\u6790\u3055\u308C\u3001\u305D\u306E\u30AF\u30E9\u30B9\u30BF\u306B\u9069\u7528\u3055\u308C\u307E\u3059\u3002 \u786C\u3044\u8868\u9762\u306E\u30B9\u30AD\u30F3\u52A0\u5DE5\u3092\u5BB9\u6613\u306B\u3057\u307E\u3059",
		"onlySel" : u"\u9078\u629E\u3057\u305F\u30B8\u30E7\u30A4\u30F3\u30C8\u306E\u52B9\u679C\u3092\u5206\u96E2\u3059\u308B\u30B3\u30F3\u30DD\u30FC\u30CD\u30F3\u30C8\u3092\u9078\u629E\u3057\u307E\u3059\u3002 \u3053\u306E\u6A5F\u80FD\u3092\u4F7F\u7528\u3059\u308B\u3068\u3001\u9078\u629E\u3057\u305F\u30B3\u30F3\u30DD\u30FC\u30CD\u30F3\u30C8\u304B\u3089\u9078\u629E\u3055\u308C\u3066\u3044\u306A\u3044\u3059\u3079\u3066\u306E\u30B8\u30E7\u30A4\u30F3\u30C8\u306E\u3059\u3079\u3066\u306E\u30A8\u30D5\u30A7\u30AF\u30C8\u304C\u524A\u9664\u3055\u308C\u307E\u3059",
		"infMesh" : u"\u73FE\u5728\u306E\u30B8\u30E7\u30A4\u30F3\u30C8\u9078\u629E\u306E\u5F71\u97FF\u3092\u53D7\u3051\u308B\u3059\u3079\u3066\u306E\u30AA\u30D6\u30B8\u30A7\u30AF\u30C8\u3092\u9078\u629E\u3057\u307E\u3059\u3002",
		},
}

def changeLanguage(inputUI, language):
	if language == None or language == "None":
		language = "english"
	inputUI.extraMenu.setTitle(  languageDict[ language ][ "extra" ]  )
	inputUI.holdAction.setText(  languageDict[ language ][ "hm" ]  )
	inputUI.fetchAction.setText(  languageDict[ language ][ "fm" ]  )
	inputUI.objSkeletonAction.setText(  languageDict[ language ][ "so" ]  )
	# inputUI.betaAction.setText(  languageDict[ language ][ "ubt" ]  )

	inputUI.skintabWidget.setTabText( 0,   languageDict[ language ][ "tools" ]  )
	inputUI.dock1.setWindowTitle (  languageDict[ language ][ "vbf00" ]  )
	inputUI.AvarageWeightButton.setText(  languageDict[ language ][ "vbf01" ]  )
	inputUI.Cop2MultVert.setText(  languageDict[ language ][ "vbf02" ]  )
	inputUI.switchVertexWeightButton.setText(  languageDict[ language ][ "vbf03" ]  )
	inputUI.jointLabelButton.setText(  languageDict[ language ][ "vbf04" ]  )
	inputUI.unifyByShellButton.setText(  languageDict[ language ][ "vbf05" ]  )
	inputUI.transfermayaskinbutton.setText(  languageDict[ language ][ "vbf06" ]  )
	inputUI.TransferPoseButton.setText(  languageDict[ language ][ "vbf07" ]  )
	inputUI.outButton.setText(  languageDict[ language ][ "vbf08" ]  )
	inputUI.inAndOutButton.setText(  languageDict[ language ][ "vbf09" ]  )
	inputUI.SmoothButton.setText(  languageDict[ language ][ "vbf10" ]  )
	inputUI.brushButton.setText(  languageDict[ language ][ "vbf11" ]  )
	inputUI.convertToJointButton.setText(  languageDict[ language ][ "vbf12" ]  )
	inputUI.Copy2BoneButton.setText(  languageDict[ language ][ "vbf13" ]  )
	inputUI.Bone2BoneSwitchButton.setText(  languageDict[ language ][ "vbf14" ]  )
	inputUI.ShowInfluencedButton.setText(  languageDict[ language ][ "vbf15" ]  )
	inputUI.deleteBoneButton.setText(  languageDict[ language ][ "vbf16" ]  )
	inputUI.addinflbutton.setText(  languageDict[ language ][ "vbf17" ]  )
	inputUI.unifyJointsButton.setText(  languageDict[ language ][ "vbf18" ]  )
	inputUI.selectInflJoints.setText(  languageDict[ language ][ "vbf19" ]  )
	inputUI.SeperateSkin.setText(  languageDict[ language ][ "vbf20" ]  )
	inputUI.keepSelectedInf.setText(  languageDict[ language ][ "vbf21" ]  )
	inputUI.getinfluencedMeshes.setText(  languageDict[ language ][ "vbf22" ]  )
	inputUI.maxInfluencesButton.setText(  languageDict[ language ][ "vbf23" ]  )
	inputUI.showInflButton.setText(  languageDict[ language ][ "vbf24" ]  )
	inputUI.resetJoints.setText(  languageDict[ language ][ "vbf25" ]  )
	inputUI.selectalljointsCheck.setText(  languageDict[ language ][ "vbf26" ]  )
	inputUI.freezeJointButton.setText(  languageDict[ language ][ "vbf27" ]  )
	inputUI.label_6.setText(  languageDict[ language ][ "vbf28" ]  )
	inputUI.saveSkinclusterButton.setText(  languageDict[ language ][ "vbf29" ]  )
	inputUI.copyVertexWeightButton.setText(  languageDict[ language ][ "vbf29" ]  )
	inputUI.loadSkinclusterButton.setText(  languageDict[ language ][ "vbf30" ]  )
	inputUI.pasteVertexWeightButton.setText(  languageDict[ language ][ "vbf30" ]  )
	inputUI.label_7.setText(  languageDict[ language ][ "vbf31" ]  )
	inputUI.label_3.setText(  languageDict[ language ][ "vbf32" ]  )
	inputUI.storeInnerSelectionButton.setText(  languageDict[ language ][ "vbf33" ]  )
	inputUI.ShrinkBorderButton.setText(  languageDict[ language ][ "vbf34" ]  )
	inputUI.GrowBorderButton.setText(  languageDict[ language ][ "vbf35" ]  )

	inputUI.dock2.setWindowTitle(  languageDict[ language ][ "ctr00" ]  )
	inputUI.label.setText(  languageDict[ language ][ "ctr01" ]  )
	inputUI.label_2.setText(  languageDict[ language ][ "ctr02" ]  )
	inputUI.transferSkinButton.setText(  languageDict[ language ][ "ctr03" ]  )
	inputUI.sourceButton.setText(  languageDict[ language ][ "ctr04" ]  )
	inputUI.targetButton.setText(  languageDict[ language ][ "ctr05" ]  )
	inputUI.copyButton.setText(  languageDict[ language ][ "ctr06" ]  )
	inputUI.resetButton.setText(  languageDict[ language ][ "ctr07" ]  )

	inputUI.dock.setWindowTitle(  languageDict[ language ][ "mt" ]  )
	inputUI.mb01.setText(  languageDict[ language ][ "mt00" ]  )
	inputUI.mb02.setText(  languageDict[ language ][ "mt01" ]  )
	inputUI.mb03.setText(  languageDict[ language ][ "mt02" ]  )
	inputUI.mb04.setText(  languageDict[ language ][ "mt03" ]  )
	inputUI.mb05.setText(  languageDict[ language ][ "mt04" ]  )
	inputUI.mb06.setText(  languageDict[ language ][ "mt05" ]  )
	inputUI.mb07.setText(  languageDict[ language ][ "mt06" ]  )
	inputUI.mb08.setText(  languageDict[ language ][ "mt07" ]  )
	inputUI.mb09.setText(  languageDict[ language ][ "mt08" ]  )
	inputUI.mb10.setText(  languageDict[ language ][ "mt09" ]  )
	inputUI.mb11.setText(  languageDict[ language ][ "mt10" ]  )
	inputUI.mb12.setText(  languageDict[ language ][ "mt11" ]  )
	inputUI.mb13.setText(  languageDict[ language ][ "mt12" ]  )
	inputUI.mb14.setText(  languageDict[ language ][ "mt13" ]  )
	inputUI.mb15.setText(  languageDict[ language ][ "mt14" ]  )
	inputUI.mb16.setText(  languageDict[ language ][ "mt15" ]  )
	inputUI.check1.setText(  languageDict[ language ][ "mt16" ]  )
	inputUI.check2.setText(  languageDict[ language ][ "mt17" ]  )

	inputUI.dock3.setWindowTitle(  languageDict[ language ][ "mvw00" ]  )
	inputUI.vertMWid.btn.setText(  languageDict[ language ][ "mvw01" ]  )
	inputUI.vertMWid.btn1.setText(  languageDict[ language ][ "mvw02" ]  )
	inputUI.skinweightWidget.source.setText(  languageDict[ language ][ "mvw03" ]  )
	inputUI.skinweightWidget.target.setText(  languageDict[ language ][ "mvw04" ]  )
	inputUI.skinweightWidget.btn.setText(  languageDict[ language ][ "mvw05" ]  )
	inputUI.skinweightWidget.btn1.setText(  languageDict[ language ][ "mvw06" ]  )
	inputUI.skinweightWidget.btn2.setText(  languageDict[ language ][ "mvw07" ]  )
	inputUI.skinweightWidget.additive.setText(  languageDict[ language ][ "mvw08" ]  )

	inputUI.skintabWidget.setTabText( 1,   languageDict[ language ][ "SEdit" ]  )
	inputUI.ReloadButton.setText(  languageDict[ language ][ "rload"  ]  )
	inputUI.LiveButton.setText(  languageDict[ language ][ "live" ]  )
	inputUI.skintabWidget.setTabText( 2,   languageDict[ language ][ "comp" ]  )
	inputUI.componentEdit.hideZero.setText(  languageDict[ language ][ "zero" ]  )
	inputUI.componentEdit.refreshBtn.setText(  languageDict[ language ][ "rload" ]  )
	inputUI.componentEdit.liveBtn.setText(  languageDict[ language ][ "live" ]  )

	inputUI.skintabWidget.setTabText( 3,   languageDict[ language ][ "wMana" ]  )
	inputUI.ExportWeights_Button.setText(  languageDict[ language ][ "wm001" ]  )
	inputUI.label_5.setText(  languageDict[ language ][ "wm002" ]  )
	inputUI.label_4.setText(  languageDict[ language ][ "wm003" ]  )
	inputUI.WorldPos_radioButton.setText(  languageDict[ language ][ "wm004" ]  )
	inputUI.UvPos_radioButton.setText(  languageDict[ language ][ "wm005" ]  )
	inputUI.ImportWeights_Button.setText(  languageDict[ language ][ "wm006" ]  )
	inputUI.DeleteWeights_Button.setText(  languageDict[ language ][ "wm007" ]  )

	# inputUI.skintabWidget.setTabText( 4,  languageDict[ language ][ "bs" ]  )
	# inputUI.groupBox.setTitle(  languageDict[ language ][ "bs001" ]  )
	# inputUI.label_12.setText(  languageDict[ language ][ "bs002" ]  )
	# inputUI.label_13.setText(  languageDict[ language ][ "bs003" ]  )
	# inputUI.skVisualiserButton.setText(  languageDict[ language ][ "bs004" ]  )
	# inputUI.label_8.setText(  languageDict[ language ][ "bs005" ]  )
	# inputUI.label_9.setText(  languageDict[ language ][ "bs006" ]  )
	# inputUI.label_10.setText(  languageDict[ language ][ "bs007" ]  )
	# inputUI.label_14.setText(  languageDict[ language ][ "bs008" ]  )
	# inputUI.label_15.setText(  languageDict[ language ][ "bs009" ]  )
	# # inputUI. .setText(  languageDict[ language ][ "bs010" ]  )
	# inputUI.label_11.setText(  languageDict[ language ][ "bs011" ]  )
	# inputUI.cullingcheckBox.setText(  languageDict[ language ][ "bs012" ]  )
	# inputUI.autoScaleCheckBox.setText(  languageDict[ language ][ "bs013" ]  )
	# inputUI.selMaskcheckBox.setText(  languageDict[ language ][ "bs014" ]  )
	# inputUI.groupBox_2.setTitle(  languageDict[ language ][ "bs015" ]  )
	# inputUI.label_16.setText(  languageDict[ language ][ "bs016" ]  )
	# inputUI.label_17.setText(  languageDict[ language ][ "bs017" ]  )
	# inputUI.skBindSkinButton.setText(  languageDict[ language ][ "bs018" ]  )
	# inputUI.groupBox_3.setTitle(  languageDict[ language ][ "bs019" ]  )
	# inputUI.analyseSelectionButton.setText(  languageDict[ language ][ "bs020" ]  )
	# inputUI.hardSkinButton.setText(  languageDict[ language ][ "bs021" ]  )
	# inputUI.softSkinButton.setText(  languageDict[ language ][ "bs022" ]  )
	# inputUI.label_18.setText(  languageDict[ language ][ "bs023" ]  )
	# inputUI.cleanSkbSceneBtn.setText(  languageDict[ language ][ "bs024" ]  )

	inputUI.dock4.setWindowTitle (  languageDict[ language ][ "smg" ]  )
	return languageDict[ language ][ "header" ] 