import bpy

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

        #トップバーのエディターメニューに項目追加
        self.layout.operator("wm.url_open_preset",text="Manual", icon="HELP")
        
    #既存のメニューにサブメニューを追加
    def submenu(self,context):

        #ID指定でサブメニューを追加
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

#Blenderに登録するクラスリスト
classes =(
    TOPBAR_MT_my_menu,
)

#オペレーター 頂点を伸ばす
class MYADDON_OT_stretch_vertex(bpy.types.Operator):
    bl_idname="myaddon.myaddon_ot_steretch_vertex"
    bl_label="頂点を伸ばす"
    bl_description="頂点座標を引っ張って伸ばします"
    #リドゥ、アンドゥ可能オプション
    bl_options={'REGISTER','UNDO'}

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