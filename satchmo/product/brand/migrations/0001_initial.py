# -*- coding: utf-8 -*-


from django.db import models, migrations

try:
    import satchmo.thumbnail.field
except ImportError:
    pass


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Brand",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text="Used for URLs", unique=True, verbose_name="Slug"
                    ),
                ),
                ("ordering", models.IntegerField(verbose_name="Ordering")),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("ordering", "slug"),
                "verbose_name": "Brand",
                "verbose_name_plural": "Brands",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="BrandTranslation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "languagecode",
                    models.CharField(
                        max_length=10,
                        verbose_name="language",
                        choices=[
                            (b"af", b"Afrikaans"),
                            (b"ar", b"Arabic"),
                            (b"ast", b"Asturian"),
                            (b"az", b"Azerbaijani"),
                            (b"bg", b"Bulgarian"),
                            (b"be", b"Belarusian"),
                            (b"bn", b"Bengali"),
                            (b"br", b"Breton"),
                            (b"bs", b"Bosnian"),
                            (b"ca", b"Catalan"),
                            (b"cs", b"Czech"),
                            (b"cy", b"Welsh"),
                            (b"da", b"Danish"),
                            (b"de", b"German"),
                            (b"el", b"Greek"),
                            (b"en", b"English"),
                            (b"en-au", b"Australian English"),
                            (b"en-gb", b"British English"),
                            (b"eo", b"Esperanto"),
                            (b"es", b"Spanish"),
                            (b"es-ar", b"Argentinian Spanish"),
                            (b"es-mx", b"Mexican Spanish"),
                            (b"es-ni", b"Nicaraguan Spanish"),
                            (b"es-ve", b"Venezuelan Spanish"),
                            (b"et", b"Estonian"),
                            (b"eu", b"Basque"),
                            (b"fa", b"Persian"),
                            (b"fi", b"Finnish"),
                            (b"fr", b"French"),
                            (b"fy", b"Frisian"),
                            (b"ga", b"Irish"),
                            (b"gl", b"Galician"),
                            (b"he", b"Hebrew"),
                            (b"hi", b"Hindi"),
                            (b"hr", b"Croatian"),
                            (b"hu", b"Hungarian"),
                            (b"ia", b"Interlingua"),
                            (b"id", b"Indonesian"),
                            (b"io", b"Ido"),
                            (b"is", b"Icelandic"),
                            (b"it", b"Italian"),
                            (b"ja", b"Japanese"),
                            (b"ka", b"Georgian"),
                            (b"kk", b"Kazakh"),
                            (b"km", b"Khmer"),
                            (b"kn", b"Kannada"),
                            (b"ko", b"Korean"),
                            (b"lb", b"Luxembourgish"),
                            (b"lt", b"Lithuanian"),
                            (b"lv", b"Latvian"),
                            (b"mk", b"Macedonian"),
                            (b"ml", b"Malayalam"),
                            (b"mn", b"Mongolian"),
                            (b"mr", b"Marathi"),
                            (b"my", b"Burmese"),
                            (b"nb", b"Norwegian Bokmal"),
                            (b"ne", b"Nepali"),
                            (b"nl", b"Dutch"),
                            (b"nn", b"Norwegian Nynorsk"),
                            (b"os", b"Ossetic"),
                            (b"pa", b"Punjabi"),
                            (b"pl", b"Polish"),
                            (b"pt", b"Portuguese"),
                            (b"pt-br", b"Brazilian Portuguese"),
                            (b"ro", b"Romanian"),
                            (b"ru", b"Russian"),
                            (b"sk", b"Slovak"),
                            (b"sl", b"Slovenian"),
                            (b"sq", b"Albanian"),
                            (b"sr", b"Serbian"),
                            (b"sr-latn", b"Serbian Latin"),
                            (b"sv", b"Swedish"),
                            (b"sw", b"Swahili"),
                            (b"ta", b"Tamil"),
                            (b"te", b"Telugu"),
                            (b"th", b"Thai"),
                            (b"tr", b"Turkish"),
                            (b"tt", b"Tatar"),
                            (b"udm", b"Udmurt"),
                            (b"uk", b"Ukrainian"),
                            (b"ur", b"Urdu"),
                            (b"vi", b"Vietnamese"),
                            (b"zh-cn", b"Simplified Chinese"),
                            (b"zh-hans", b"Simplified Chinese"),
                            (b"zh-hant", b"Traditional Chinese"),
                            (b"zh-tw", b"Traditional Chinese"),
                        ],
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="title")),
                (
                    "short_description",
                    models.CharField(
                        max_length=200, verbose_name="Short Description", blank=True
                    ),
                ),
                (
                    "description",
                    models.TextField(verbose_name="Full Description", blank=True),
                ),
                (
                    "picture",
                    models.ImageField(
                        max_length=200, null=True, verbose_name="Picture", blank=True
                    ),
                ),
                (
                    "brand",
                    models.ForeignKey(
                        related_name="translations",
                        to="brand.Brand",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "ordering": ("languagecode",),
                "verbose_name": "Brand Translation",
                "verbose_name_plural": "Brand Translations",
            },
            bases=(models.Model,),
        ),
    ]
