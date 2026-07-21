import bpy
import math
import bpy_extras
import gpu
import gpu_extras.batch
import copy
import mathutils


# ブレンダーに登録するアドオン情報
bl_info = {
    "name":"レベルエディタ",
    "author":"Tanabe",
    "version":(1,0),
    "blender":(3,6,1),
    "location":"",
    "description":"レベルエディタ",
    "warning":"",
    "wiki_url":"",
    "tracker_url":"",
    "category":"Object"
}

# メニュー項目描画
def draw_menu_manual(self,context):
    #self : 呼び出し元のクラスインスタンス C++でいうthisポインタ

    #トップバーのエディターメニューに項目追加
    self.layout.operator("wm.url_open_preset",text="Manual", icon="HELP")

#トップバーの拡張メニュー
class TOPBAR_MT_my_menu(bpy.types.Menu):
    #Blenderがクラスを識別する為の固有文字列
    bl_idname = "TOPBAR_MT_my_menu"

    #メニューのラベルとして表示される文字列
    bl_label = "MyMenu"

    #著者表示用の文字列
    bl_description= "拡張メニュー by" + bl_info["author"]

    #サブメニューの描画
    def draw(self,context):

        #トップバーのエディターメニューに項目を追加
        self.layout.operator(MYADDON_OT_export_scene.bl_idname,
            text=MYADDON_OT_export_scene.bl_label)

         #トップバーのエディターメニューに項目を追加
        self.layout.operator(MYADDON_OT_create_sphere.bl_idname,
            text=MYADDON_OT_create_sphere.bl_label)

        #トップバーのエディターメニューに項目を追加
        self.layout.operator(MYADDON_OT_stretch_vertex.bl_idname,
            text=MYADDON_OT_stretch_vertex.bl_label)

        #トップバーのエディターメニューに項目追加
        self.layout.operator("wm.url_open_preset",text="Manual", icon="HELP")
        
    #既存のメニューにサブメニューを追加
    def submenu(self,context):

        #ID指定でサブメニューを追加
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

#オペレーター 頂点を伸ばす
class MYADDON_OT_stretch_vertex(bpy.types.Operator):
    bl_idname="myaddon.myaddon_ot_stretch_vertex"
    bl_label="頂点を伸ばす"
    bl_description="頂点座標を引っ張って伸ばします"
    #リドゥ、アンドゥ可能オプション
    bl_options={'REGISTER','UNDO'}

    #メニューを実行した時に呼ばれるコールバック関数
    def execute(self,context):
        bpy.data.objects["Cube"].data.vertices[0].co.x += 1.0
        print("頂点を伸ばしました")

        #オペレーターの命令終了
        return {"FINISHED"}

#オペレーター ICO球生成
class MYADDON_OT_create_sphere(bpy.types.Operator):
    bl_idname = "myaddon.create_sphere"
    bl_label = "ICO球を生成します"
    bl_options = {"REGISTER","UNDO"}

    #メニューを実行した時に呼ばれる関数
    def execute(self,context):
        bpy.ops.mesh.primitive_ico_sphere_add()
        print("ICO球を生成しました")

        return{"FINISHED"}
    
class MYADDON_OT_export_scene(bpy.types.Operator,bpy_extras.io_utils.ExportHelper):
    bl_idname = "myaddon.myaddon_ot_export_scene"
    bl_label = "シーン出力"
    bl_description = "シーン情報をExportします"

    filename_ext = ".scene"

    def execute(self, context):

        print("シーン情報をExportします")

        self.export()

        self.report({"INFO"}, "シーン情報をExportしました")

        return {'FINISHED'}
    
    def write_and_print(self, file, text):
        file.write(text)
        file.write("\n")
        print(text)

    def export(self):

        print("シーン情報出力開始... %r" % self.filepath)

        with open(self.filepath, "wt") as file:

            file.write("SCENE\n")

            # シーン内の全オブジェクトについて
            for obj in bpy.context.scene.objects:

                if(obj.parent):
                    continue
                self.parse_scene_recursive(file,obj,0)

    def parse_scene_recursive(self, file, obj, level):

        indent = "\t" * level

        self.write_and_print(file, indent + obj.type)

        trans, rot, scale = obj.matrix_local.decompose()

        rot = rot.to_euler()

        rot.x = math.degrees(rot.x)
        rot.y = math.degrees(rot.y)
        rot.z = math.degrees(rot.z)

        self.write_and_print(file, indent + "Trans(%f,%f,%f)" % (trans.x, trans.y, trans.z))
        self.write_and_print(file, indent + "Rot(%f,%f,%f)" % (rot.x, rot.y, rot.z))
        self.write_and_print(file, indent + "Scale(%f,%f,%f)" % (scale.x, scale.y, scale.z))

        if "file_name" in obj:
            self.write_and_print(file, indent + "N %s" % obj["file_name"])

        #カスタムプロパティ"collider"
        if "collider" in obj:
            self.write_and_print(file, indent + "C %s" % obj["collider"])
            temp_str = indent + "CC %f %f %f"
            temp_str %= (
                obj["collider_center"][0],
                obj["collider_center"][1],
                obj["collider_center"][2]
            )
            self.write_and_print(file, temp_str)
            temp_str = indent + "CS %f %f %f"
            temp_str %= (
                obj["collider_size"][0],
                obj["collider_size"][1],
                obj["collider_size"][2]
            )
            self.write_and_print(file, temp_str)

        self.write_and_print(file, indent + "END")
        self.write_and_print(file, "")

        for child in obj.children:
            self.parse_scene_recursive(file, child, level + 1)

class OBJECT_PT_file_name(bpy.types.Panel):
    """オブジェクトのファイルネームパネル"""
    bl_idname = "OBJECT_PT_file_name"
    bl_label = "FileName"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    #サブメニューの描画
    def draw(self,context):
        #パネルに項目を追加
        if "file_name" in context.object:
            #既にプロパティがあれば表示
            self.layout.prop(context.object,'["file_name"]',text=self.bl_label)
        else:
            #プロパティがなければプロパティ追加ボタン表示
            self.layout.operator(MYADDON_OT_add_filename.bl_idname) 

#オペレーター カスタムプロパティ ファイルネーム追加
class MYADDON_OT_add_filename(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_add_filename"
    bl_label = "FileName 追加"
    bl_description = "['file_name']カスタムプロパティを追加します"
    bl_options ={"REGISTER","UNDO"}

    def execute(self,context):

        #カスタムプロパティを追加
        context.object["file_name"] = ""
        return {"FINISHED"}
    
# コライダー描画
class DrawCollider:

    #描画ハンドル
    handle = None

    @staticmethod
    #3Dビューに登録する描画関数
    def draw_collider():
       
       #頂点データ
       vertices ={"pos":[]} 

       #インデックスデータ
       indices = []

       #各頂点の中心からのオフセット
       offsets = [
            [-0.5,-0.5,-0.5], #左下前
            [+0.5,-0.5,-0.5], #右下前
            [-0.5,+0.5,-0.5], #左上前
            [+0.5,+0.5,-0.5], #右上前
            [-0.5,-0.5,+0.5], #左下奥
            [+0.5,-0.5,+0.5], #右下奥
            [-0.5,+0.5,+0.5], #左上奥
            [+0.5,+0.5,+0.5], #右上奥
       ]

       #立方体のX,Y,Z方向サイズ
       size = [2,2,2]

       for obj in bpy.context.scene.objects:
           
            #コライダープロパティがなければ描画をスキップ
            if not "collider" in obj:
                continue

            #中心点、サイズの変数を宣言
            center = mathutils.Vector((0,0,0))
            size = mathutils.Vector((2,2,2))

            #プロパティから値を取得
            center[0] = obj["collider_center"][0]
            center[1] = obj["collider_center"][1]
            center[2] = obj["collider_center"][2]
            size[0] = obj["collider_size"][0]
            size[1] = obj["collider_size"][1]
            size[2] = obj["collider_size"][2]

            #追加前の頂点数
            start = len(vertices["pos"])

            #boxの８頂点分回す
            for offset in offsets:
                pos = copy.copy(center)
                #中心点の座標をコピー
                pos[0]+=offset[0]*size[0]
                pos[1]+=offset[1]*size[1]
                pos[2]+=offset[2]*size[2]

                #ローカル座標からワールド座標に変換
                pos = obj.matrix_world @ pos

                #頂点データリストに座標を追加
                vertices['pos'].append(pos)
               
            indices.extend([
                   
                #前面を構成
                [start+0,start+1],
                [start+2,start+3],
                [start+0,start+2],
                [start+1,start+3],
                   
                #奥面を構成
                [start+4,start+5],
                [start+6,start+7],
                [start+4,start+6],
                [start+5,start+7],

                #手前と奥を繋ぐ辺
                [start+0,start+4],
                [start+1,start+5],
                [start+2,start+6],
                [start+3,start+7],
            ])
               
       #ビルトインシェーダーを取得
       shader = gpu.shader.from_builtin("UNIFORM_COLOR")

       #バッチを作成
       batch = gpu_extras.batch.batch_for_shader(shader,"LINES",vertices,indices = indices)

       #シェーダーのパラメータを設定
       color=[0.5,1.0,1.0,1.0]
       shader.bind()
       shader.uniform_float("color",color)

       #描画
       batch.draw(shader)

#オペレーターカスタムプロパティ　コライダーを追加
class MYADDON_OT_add_collider(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_add_collider"
    bl_label = "コライダー追加"
    bl_description = "['collider']カスタムプロパティを追加します"
    bl_options = {"REGISTER","UNDO"}
    
    def execute(self,context):

        #カスタムプロパティを追加
        context.object["collider"]= "BOX"
        context.object["collider_center"] = mathutils.Vector((0,0,0))
        context.object["collider_size"] = mathutils.Vector((2,2,2))
        return {"FINISHED"}

#パネルコライダー
class OBJECT_PT_collider(bpy.types.Panel):
    bl_idname = "OBJECT_PT_collider"
    bl_label = "Collider"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    #サブメニュー描画
    def draw(self,context):

        #パネルに項目を追加
        if "collider" in context.object:
            
            #既にプロパティがあれば、プロパティを描画
            self.layout.prop(context.object,'["collider"]',text= "Type")
            self.layout.prop(context.object,'["collider_center"]',text="Center")
            self.layout.prop(context.object,'["collider_size"]',text="Size")
        else:
            #プロパティがなければプロパティ追加ボタン表示
            self.layout.operator(MYADDON_OT_add_collider.bl_idname)

#C++でいうここからがメインループ 上がグローバル関数等
#Blenderに登録するクラスリスト
classes =(
    MYADDON_OT_export_scene,
    MYADDON_OT_create_sphere,
    MYADDON_OT_stretch_vertex,
    TOPBAR_MT_my_menu,
    MYADDON_OT_add_filename,
    OBJECT_PT_file_name,
    MYADDON_OT_add_collider,
    OBJECT_PT_collider
)

#アドオン有効時のコールバック
def register():
    #Blenderにクラスを登録
    for cls in classes:
        bpy.utils.register_class(cls)

    #メニューに項目追加
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)

    #3Dビューに描画関数追加
    DrawCollider.handle = bpy.types.SpaceView3D.draw_handler_add(DrawCollider.draw_collider,(),"WINDOW","POST_VIEW")
    print("レベルエディタが有効化されました")

def unregister():

    bpy.types.TOPBAR_MT_editor_menus.remove(
        TOPBAR_MT_my_menu.submenu
    )

    bpy.types.SpaceView3D.draw_handler_remove(
        DrawCollider.handle,
        "WINDOW"
    )

    for cls in reversed(classes):
        print("unregister ->", cls.__name__)

        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print("FAILED ->", cls.__name__)
            print(e)

    print("レベルエディタが無効化されました")
    
if __name__ == "__main__":
    register()