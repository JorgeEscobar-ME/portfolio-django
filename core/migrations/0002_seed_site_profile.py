from django.db import migrations


def create_site_profile(apps, schema_editor):
    SiteProfile = apps.get_model("core", "SiteProfile")
    database = schema_editor.connection.alias
    SiteProfile.objects.using(database).update_or_create(
        pk=1,
        defaults={
            "name": "Jorge Alejandro Escobar Zúñiga",
            "headline": (
                "MSc. en Recursos Digitales Aplicados a la Educación. "
                "Estudiante de la Maestría en Matemática, UTP"
            ),
            "biography": (
                "Soy alguien que tiene mucha pasión por el conocimiento en "
                "múltiples disciplinas. Como amo enseñar, decidí llevar mis "
                "conocimientos al siguiente nivel con la Maestría en Matemática "
                "de la Universidad Tecnológica de Pereira. En mi pregrado estudié "
                "Ingeniería Mecánica. Amo la ciencia de datos. Mis áreas de interés "
                "son los sistemas dinámicos no lineales, las ecuaciones diferenciales, "
                "la educación matemática y el desarrollo de software, especialmente "
                "con Python. Me gustan las ciencias naturales, en particular la física "
                "y la biología."
            ),
            "public_email": "jorgealejandroescobar0@gmail.com",
            "github_url": "https://github.com/JorgeEscobar-ME",
            "linkedin_url": "https://www.linkedin.com/in/jorgeescobarz/",
        },
    )


def remove_site_profile(apps, schema_editor):
    SiteProfile = apps.get_model("core", "SiteProfile")
    SiteProfile.objects.using(schema_editor.connection.alias).filter(pk=1).delete()


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]

    operations = [migrations.RunPython(create_site_profile, remove_site_profile)]