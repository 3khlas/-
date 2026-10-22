import os
import gradio as gr
from data import COLUMNS
from functions import *

CSS='''body{direction:rtl;text-align:right}.gradio-container{max-width:1450px!important}@media(max-width:700px){.gradio-container{padding:8px!important}.gr-button{min-height:44px}.gr-dataframe{font-size:12px}} .title{text-align:center}.card{text-align:center;padding:15px;border-radius:14px}'''

def login_action(u,p):
    ok,role=authenticate(u,p)
    if ok:return gr.update(visible=False),gr.update(visible=True),f'✅ تم الدخول بنجاح — الصلاحية: **{role}**',u,role
    return gr.update(visible=True),gr.update(visible=False),'❌ اسم المستخدم أو كلمة المرور غير صحيحة.','',''

def do_search(q,d,y):
    x=search(q,d,y); return f'### 🔎 عدد النتائج: {len(x)}',x

def dashboard():
    total,counts=stats(); return f'## 👥 إجمالي الخريجين: {total}', {str(k):int(v) for k,v in counts.items()}

def detail(reg):
    s=get_student(reg)
    if not s:return '❌ لم يتم العثور على الخريج.'
    return '\n'.join([f'## 🎓 {s["الاسم"]}',f'**رقم التسجيل:** {s["رقم التسجيل"]}  ',f'**الرقم الجامعي:** {s["الرقم الجامعي"]}  ',f'**القسم:** {s["القسم"]}  ',f'**التخصص:** {s["التخصص"]}  ',f'**المعدل:** {s["المعدل التراكمي"]}  ',f'**المرتبة:** {s["تصنيف المرتبة"]}  ',f'**سنة التخرج:** {s["سنة التخرج"]}  ',f'**الإيميل:** {s["الإيميل"]}  ',f'**الهاتف:** {s["الهاتف"]}  ',f'**مشروع التخرج:** {s["مشروع التخرج"]}'])

def clear_edit(): return ('',)*12

with gr.Blocks(title='نظام إدارة خريجي جامعة البطانة',css=CSS,theme=gr.themes.Soft()) as demo:
    gr.Markdown('# 🎓 نظام إدارة خريجي جامعة البطانة',elem_classes=['title'])
    with gr.Accordion('🌐 بوابة الخريج العامة — بدون تسجيل دخول', open=True):
        gr.Markdown('يمكن لأي خريج الاستعلام عن بياناته باستخدام رقم التسجيل فقط.')
        pubreg=gr.Textbox(label='رقم التسجيل')
        pubbtn=gr.Button('🔎 استعلام عام',variant='primary')
        pubout=gr.Markdown()
        pubbtn.click(public_search,pubreg,pubout)
    login_box=gr.Group()
    with login_box:
        gr.Markdown('## 🔐 تسجيل الدخول')
        user=gr.Textbox(label='اسم المستخدم',value='admin'); pw=gr.Textbox(label='كلمة المرور',type='password',value='1234'); lb=gr.Button('🔐 دخول',variant='primary'); ls=gr.Markdown()
    main=gr.Group(visible=False)
    with main:
        session_user=gr.State(''); session_role=gr.State('')
        dash=gr.Markdown()
        with gr.Row():
            refresh=gr.Button('🔄 تحديث لوحة التحكم'); logout=gr.Button('🚪 تسجيل الخروج')
        with gr.Tabs():
            with gr.Tab('📊 لوحة التحكم'):
                chart=gr.JSON(label='توزيع الخريجين حسب القسم'); alltable=gr.Dataframe(headers=COLUMNS,interactive=False,wrap=True)
                gr.Markdown('### 📈 إحصائيات سريعة')
                stat=gr.Markdown()
                refresh.click(lambda: (dashboard()[0],dashboard()[1],search()),outputs=[dash,chart,alltable])
            with gr.Tab('🔎 البحث المتقدم'):
                with gr.Row(): q=gr.Textbox(label='بحث شامل'); d=gr.Dropdown(departments(),value='الكل',label='القسم'); y=gr.Dropdown(years(),value='الكل',label='سنة التخرج')
                sb=gr.Button('🔍 بحث',variant='primary'); ss=gr.Markdown(); table=gr.Dataframe(headers=COLUMNS,interactive=False,wrap=True)
                sb.click(do_search,[q,d,y],[ss,table]); q.submit(do_search,[q,d,y],[ss,table])
                gr.Markdown('### 🎓 عرض خريج بالتفصيل'); regdetail=gr.Textbox(label='رقم التسجيل'); detailbtn=gr.Button('عرض التفاصيل'); detailout=gr.Markdown(); detailbtn.click(detail,regdetail,detailout)
            with gr.Tab('➕ إضافة خريج'):
                with gr.Row(): a1=gr.Textbox(label='رقم التسجيل *'); a2=gr.Textbox(label='الرقم الجامعي'); a3=gr.Textbox(label='الاسم *')
                with gr.Row(): a4=gr.Dropdown(departments()[1:],label='القسم'); a5=gr.Textbox(label='التخصص'); a6=gr.Number(label='المعدل'); a7=gr.Textbox(label='تصنيف المرتبة'); a8=gr.Number(label='سنة التخرج',precision=0,value=2026)
                with gr.Row(): a9=gr.Textbox(label='الإيميل'); a10=gr.Textbox(label='الهاتف'); a11=gr.Textbox(label='مشروع التخرج')
                a12=gr.File(label='صورة الخريج',type='filepath'); addb=gr.Button('➕ حفظ',variant='primary'); adds=gr.Markdown()
                addb.click(lambda *v:add_student(v,v[-1] if False else 'admin'),[a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12],[adds,table])
            with gr.Tab('✏️ تعديل / 🗑️ حذف'):
                e1=gr.Textbox(label='رقم التسجيل')
                with gr.Row(): e2=gr.Textbox(label='الرقم الجامعي'); e3=gr.Textbox(label='الاسم'); e4=gr.Dropdown(departments()[1:],label='القسم'); e5=gr.Textbox(label='التخصص')
                with gr.Row(): e6=gr.Number(label='المعدل'); e7=gr.Textbox(label='تصنيف المرتبة'); e8=gr.Number(label='سنة التخرج',precision=0); e9=gr.Textbox(label='الإيميل'); e10=gr.Textbox(label='الهاتف')
                e11=gr.Textbox(label='مشروع التخرج'); e12=gr.File(label='الصورة',type='filepath')
                with gr.Row(): ub=gr.Button('💾 حفظ التعديل',variant='primary'); db=gr.Button('🗑️ حذف',variant='stop')
                es=gr.Markdown(); ub.click(lambda *v:update_student(v),[e1,e2,e3,e4,e5,e6,e7,e8,e9,e10,e11,e12],[es,table]); db.click(delete_student,e1,[es,table])
            with gr.Tab('📥 Excel والتقارير'):
                gr.Markdown('استيراد ملف Excel يستبدل قاعدة البيانات الحالية بعد التحقق.'); imp=gr.File(label='ملف Excel',type='filepath'); ib=gr.Button('📥 استيراد'); ims=gr.Markdown(); ib.click(import_excel,imp,[ims,alltable]); dl=gr.DownloadButton('⬇️ تصدير Excel'); dl.click(export_excel,outputs=dl)
                backup=gr.Button('💾 إنشاء نسخة احتياطية'); bo=gr.File(label='ملف النسخة الاحتياطية'); backup.click(backup_database,outputs=bo)
                gr.Markdown('### 🖨️ تقرير خريج'); preg=gr.Textbox(label='رقم التسجيل'); pdf=gr.DownloadButton('⬇️ إنشاء/تحميل تقرير PDF');
                def make_pdf(reg):
                    from reportlab.pdfgen import canvas
                    from reportlab.lib.pagesizes import A4
                    s=get_student(reg)
                    if not s:return None
                    path=os.path.join(os.path.dirname(__file__),f'graduate_{reg}.pdf'); c=canvas.Canvas(path,pagesize=A4); y0=780
                    try:
                        from reportlab.pdfbase import pdfmetrics
                        from reportlab.pdfbase.ttfonts import TTFont
                        font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
                        if os.path.exists(font): pdfmetrics.registerFont(TTFont('ArabicFont',font)); c.setFont('ArabicFont',14)
                        else: c.setFont('Helvetica',12)
                    except Exception: c.setFont('Helvetica',12)
                    c.drawCentredString(300,y0,'جامعة البطانة - سجل خريج'); y0-=40; c.setFont('ArabicFont' if 'ArabicFont' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',11)
                    for k,v in s.items():
                        if k=='الصورة': continue
                        c.drawString(60,y0,f'{k}: {v}'); y0-=24
                    c.save(); return path
                pdf.click(make_pdf,preg,pdf)
            with gr.Tab('👥 المستخدمون') as users_tab:
                gr.Markdown('إدارة المستخدمين متاحة للمدير.'); ul=gr.Dataframe(value=users_list(),interactive=False); nu=gr.Textbox(label='اسم المستخدم الجديد'); np=gr.Textbox(label='كلمة المرور'); nr=gr.Dropdown(['مدير','موظف','عرض فقط'],value='موظف',label='الصلاحية'); ub2=gr.Button('➕ إضافة مستخدم'); ud=gr.Textbox(label='اسم المستخدم للحذف'); db2=gr.Button('🗑️ حذف مستخدم'); us=gr.Markdown(); ub2.click(lambda u,p,r:add_user(u,p,r,'admin'),[nu,np,nr],[us,ul]); db2.click(lambda u:delete_user(u,'admin'),ud,[us,ul])
            with gr.Tab('🧾 سجل التدقيق'):
                al=gr.Dataframe(value=audit(),interactive=False); ab=gr.Button('🔄 تحديث السجل'); ab.click(audit,outputs=al)
        gr.Markdown('**بيانات الدخول الافتراضية:** admin / 1234')
    lb.click(login_action,[user,pw],[login_box,main,ls,session_user,session_role])
    logout.click(lambda:(gr.update(visible=True),gr.update(visible=False),''),outputs=[login_box,main,ls])

if __name__=='__main__':
    demo.launch()
