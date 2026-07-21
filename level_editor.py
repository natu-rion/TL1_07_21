import bpy
import math
import bpy_extras

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
    bl_idname = "myaddon.myaddon_ot_create_object"
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
            for object in bpy.context.scene.objects:

                if(object.parent):
                    continue
                self.parse_scene_recursive(file,object,0)

    def parse_scene_recursive(self,file,object,level):
        """シーン解析再帰関数"""

        self.write_and_print(file, object.type + "-"+object.name)
        trans, rot, scale= object.matrix_local.decompose()

        #
        rot = rot.to_euler()

        #
        rot.x = math.degrees(rot.x)
        rot.y = math.degrees(rot.y)
        rot.z = math.degrees(rot.z)

        #深さ分インデントする
        indent = ""
        for i in range(level):
            indent += "\t"

        #トランスフォーム情報
        self.write_and_print(file,indent + "Trans(%f,%f,%f)" % (trans.x,trans.y,trans.z))
        self.write_and_print(file,indent +"Rot(%f,%f,%f)" % (rot.x,rot.y,rot.z))
        self.write_and_print(file,indent +"Scale(%f,%f,%f)" % (scale.x,scale.y,scale.z))
        self.write_and_print(file,"")

        #子ノードに進む
        for child in object.children:
            self.parse_scene_recursive(file,child,level +1)

#C++でいうここからがメインループ 上がグローバル関数等
#Blenderに登録するクラスリスト
classes =(
    MYADDON_OT_export_scene,
    MYADDON_OT_create_sphere,
    MYADDON_OT_stretch_vertex,
    TOPBAR_MT_my_menu,
)

#アドオン有効時のコールバック
def register():
    #Blenderにクラスを登録
    for cls in classes:
        bpy.utils.register_class(cls)

    #メニューに項目追加
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)
    print("レベルエディタが有効化されました")

def unregister():
    #メニューから項目削除
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)

    #Blenderクラスから削除
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("レベルエディタが無効化されました")
    
if __name__ == "__main__":
    register()