# Generated by Django 5.1.4 on 2025-01-03 13:20

import django.core.validators
import django.db.models.deletion
import gelfmp.models.charcoal_contract
import gelfmp.models.dcf
import gelfmp.models.document
import gelfmp.utils.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='State',
            fields=[
                ('abbr', models.CharField(max_length=2, primary_key=True, serialize=False, verbose_name='Sigla')),
                ('name', models.CharField(max_length=100, verbose_name='Nome')),
            ],
            options={
                'verbose_name': 'Estado',
                'verbose_name_plural': 'Estados',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nome')),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gelfmp.state', verbose_name='Estado')),
            ],
            options={
                'verbose_name': 'Cidade',
                'verbose_name_plural': 'Cidades',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('corporate_name', models.CharField(help_text='Insira nomes padronizados para evitar inconsistência, como o próprio nome que consta no CNPJ.', max_length=200, unique=True, verbose_name='Razão Social')),
                ('rm_code', models.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name='Código RM')),
                ('active', models.BooleanField(default=True, verbose_name='Fornecedor Ativo')),
                ('material_type', models.CharField(choices=[('Minério de Ferro', 'Minério de Ferro'), ('Subprodutos', 'Subprodutos'), ('Carvão Vegetal', 'Carvão Vegetal'), ('Bauxita', 'Bauxita'), ('Argila', 'Argila'), ('Areia', 'Areia'), ('Calcario', 'Calcario'), ('FeSiMg', 'FeSiMg'), ('Ferroligas', 'Ferroligas'), ('Mistura', 'Mistura'), ('Fluorita', 'Fluorita'), ('Dolomita', 'Dolomita'), ('Grafite', 'Grafite')], max_length=100, verbose_name='Tipo de Material')),
                ('supplier_type', models.CharField(blank=True, choices=[('gelf', 'GELF'), ('botumirim', 'Botumirim'), ('third_party', 'Terceiro')], max_length=100, null=True, verbose_name='Tipo de Fornecedor (Carvão)')),
                ('distance_in_meters', models.IntegerField(blank=True, null=True, verbose_name='Distância em Metros')),
                ('address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Endereço')),
                ('cep', models.CharField(max_length=10, validators=[django.core.validators.RegexValidator(message='Insira um CEP válido. Use o formato 00000000 ou 00000-000.', regex='^(\\d{8}|\\d{5}-\\d{3})$')], verbose_name='CEP')),
                ('latitude', models.DecimalField(blank=True, decimal_places=8, max_digits=11, null=True, validators=[gelfmp.utils.validators.validate_latitude])),
                ('longitude', models.DecimalField(blank=True, decimal_places=8, max_digits=11, null=True, validators=[gelfmp.utils.validators.validate_longitude])),
                ('state_registration', models.CharField(blank=True, max_length=50, null=True, verbose_name='Inscrição Estadual')),
                ('municipal_registration', models.CharField(blank=True, max_length=50, null=True, verbose_name='Inscrição Municipal')),
                ('xml_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email XML')),
                ('cpf_cnpj', models.CharField(max_length=18, unique=True, validators=[django.core.validators.RegexValidator(message='Insira um CPF ou CNPJ válido. Use apenas numeros ou 000.000.000-00, 00.000.000/0000-00.', regex='^(\\w{14}|\\d{11}|\\d{3}.\\d{3}.\\d{3}-\\d{2}|\\d{2}.\\d{3}.\\d{3}/\\d{4}-\\d{2})$')], verbose_name='CPF ou CNPJ')),
                ('observations', models.TextField(blank=True, help_text='Adicione informações adicionais ou observações relevantes.', max_length=2000, null=True, verbose_name='Observações')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='suppliers', to='gelfmp.city', verbose_name='Cidade')),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='suppliers', to='gelfmp.state', verbose_name='Estado')),
            ],
            options={
                'verbose_name': 'Fornecedor',
                'verbose_name_plural': 'Fornecedores',
                'ordering': ['corporate_name'],
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('name', models.CharField(blank=True, help_text='Caso não informado, o nome do arquivo será usado para preencher este campo.', max_length=50, verbose_name='Nome de Exibição')),
                ('file', models.FileField(max_length=255, upload_to=gelfmp.models.document.Document.upload_to, validators=[gelfmp.utils.validators.validate_max_file_size], verbose_name='Arquivo')),
                ('geojson', models.JSONField(blank=True, help_text='Este campo é gerado automaticamente ao subir um Shapefile e não deve ser alterado manualmente.', null=True, verbose_name='GeoJSON')),
                ('validity', models.DateField(blank=True, help_text='Caso não informado e o nome do arquivo contém a data, ela será usada para preencher este campo.\nExemplo: nome do arquivo CTF_02.05.2020.pdf, a data 02/05/2020 será usada.', null=True, verbose_name='Validade')),
                ('document_type', models.CharField(choices=[('ctf', 'CADASTRO TÉCNICO FEDERAL'), ('lic_ambiental', 'LICENÇA AMBIENTAL'), ('exemption', 'DISPENSA'), ('reg_ief', 'REGISTRO IEF'), ('car', 'CADASTRO AMBIENTAL RURAL'), ('shapefile', 'SHAPEFILE'), ('property_shapefile', 'SHAPEFILE DE PROPRIEDADE'), ('other', 'OUTRO')], max_length=50, verbose_name='Tipo de Documento')),
                ('visible', models.BooleanField(default=True, verbose_name='Visível')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='documents', to='gelfmp.supplier', verbose_name='Fornecedor')),
            ],
            options={
                'verbose_name': 'Documento',
                'verbose_name_plural': 'Documentos',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DCF',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('process_number', models.CharField(max_length=50, validators=[django.core.validators.RegexValidator(message='Insira um valor válido, usando o formato 0000000000000/00-00.', regex='^\\d{13}/\\d{2}-\\d{2}$')], verbose_name='Número do Processo')),
                ('declared_volume', models.IntegerField(blank=True, null=True, verbose_name='Volume Declarado (m³)')),
                ('available_volume', models.IntegerField(blank=True, null=True, verbose_name='Volume Disponível (m³)')),
                ('issue_date', models.DateField(blank=True, null=True, verbose_name='Data de Emissão')),
                ('validity_date', models.DateField(blank=True, editable=False, null=True, verbose_name='Data de Vencimento')),
                ('file', models.FileField(blank=True, null=True, upload_to=gelfmp.models.dcf.DCF.upload_to, validators=[gelfmp.utils.validators.validate_max_file_size], verbose_name='Arquivo DCF')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dcfs', to='gelfmp.supplier', verbose_name='Fornecedor')),
            ],
            options={
                'verbose_name': 'DCF',
                'verbose_name_plural': 'DCFs',
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('name', models.CharField(max_length=200, verbose_name='Nome')),
                ('cpf', models.CharField(blank=True, max_length=14, null=True, validators=[django.core.validators.RegexValidator(message='Insira um CPF ou CNPJ válido. Use apenas numeros ou 000.000.000-00, 00.000.000/0000-00.', regex='^(\\w{14}|\\d{11}|\\d{3}.\\d{3}.\\d{3}-\\d{2}|\\d{2}.\\d{3}.\\d{3}/\\d{4}-\\d{2})$')], verbose_name='CPF')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('contact_type', models.CharField(choices=[('witness', 'Testemunha'), ('legal_representative', 'Representante Legal'), ('accounting_responsible', 'Setor Contábil'), ('financial_responsible', 'Setor Financeiro'), ('negotiation_responsible', 'Negociação (Comercial)'), ('nf_responsible', 'Emissão de Notas Fiscais'), ('logistics_responsible', 'Programação e Logística'), ('other', 'Outro')], max_length=50, verbose_name='Função')),
                ('primary_phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Telefone Principal')),
                ('secondary_phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Telefone Secundário')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='gelfmp.supplier', verbose_name='Fornecedor')),
            ],
            options={
                'verbose_name': 'Contato',
                'verbose_name_plural': 'Contatos',
            },
        ),
        migrations.CreateModel(
            name='CharcoalMonthlyPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('planned_volume', models.FloatField(verbose_name='Volume Programado (m³)')),
                ('month', models.IntegerField(choices=[(1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'), (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')], verbose_name='Mês')),
                ('year', models.IntegerField(choices=[(2026, '2026'), (2025, '2025'), (2024, '2024'), (2023, '2023'), (2022, '2022'), (2021, '2021'), (2020, '2020')], verbose_name='Ano')),
                ('price', models.DecimalField(blank=True, decimal_places=2, help_text='Somente aplicável a GELF.', max_digits=6, null=True, verbose_name='Preço (R$)')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='monthly_plans', to='gelfmp.supplier', verbose_name='Fornecedor')),
            ],
            options={
                'verbose_name': 'Programação de Carvão',
                'verbose_name_plural': 'Programações de Carvão',
            },
        ),
        migrations.CreateModel(
            name='CharcoalIQF',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('iqf', models.FloatField(verbose_name='IQF')),
                ('planned_percentage', models.FloatField(validators=[gelfmp.utils.validators.validate_percentage], verbose_name='Programação Realizada (%)')),
                ('fines_percentage', models.FloatField(validators=[gelfmp.utils.validators.validate_percentage], verbose_name='Finos (%)')),
                ('moisture_percentage', models.FloatField(validators=[gelfmp.utils.validators.validate_percentage], verbose_name='Umidade (%)')),
                ('density_percentage', models.FloatField(validators=[gelfmp.utils.validators.validate_percentage], verbose_name='Densidade (%)')),
                ('volume_density_below_min', models.FloatField(verbose_name='Volume com Densidade Fora (m³)')),
                ('volume_fines_above_max', models.FloatField(verbose_name='Volume com Finos Fora (m³)')),
                ('volume_moisture_above_max', models.FloatField(verbose_name='Volume com Umidade Fora (m³)')),
                ('planned_volume', models.FloatField(verbose_name='Volume Programado (m³)')),
                ('total_volume', models.FloatField(verbose_name='Volume Total (m³)')),
                ('month', models.IntegerField(choices=[(1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'), (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')], verbose_name='Mês')),
                ('year', models.IntegerField(choices=[(2026, '2026'), (2025, '2025'), (2024, '2024'), (2023, '2023'), (2022, '2022'), (2021, '2021'), (2020, '2020')], verbose_name='Ano')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='iqfs', to='gelfmp.supplier', verbose_name='Fornecedor')),
            ],
            options={
                'verbose_name': 'IQF de Fornecedor de Carvão',
                'verbose_name_plural': 'IQFs de Fornecedores de Carvão',
                'ordering': ['-year', '-month'],
            },
        ),
        migrations.CreateModel(
            name='CharcoalEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('origin_ticket', models.CharField(max_length=50, unique=True, verbose_name='Ticket de Origem')),
                ('vehicle_plate', models.CharField(max_length=50, verbose_name='Placa do Veículo')),
                ('origin_volume', models.FloatField(verbose_name='Volume de Origem (m³)')),
                ('entry_volume', models.FloatField(verbose_name='Volume de Entrada (m³)')),
                ('entry_date', models.DateField(verbose_name='Data de Entrada')),
                ('moisture', models.FloatField(verbose_name='Umidade (%)')),
                ('fines', models.FloatField(verbose_name='Finos (%)')),
                ('density', models.FloatField(verbose_name='Densidade')),
                ('gcae', models.CharField(max_length=50, verbose_name='GCAE')),
                ('dcf', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='charcoal_entries', to='gelfmp.dcf', verbose_name='DCF')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='charcoal_entries', to='gelfmp.supplier', verbose_name='Fornecedor')),
            ],
            options={
                'verbose_name': 'Entrada de Carvão',
                'verbose_name_plural': 'Entradas de Carvão',
                'ordering': ['-entry_date'],
            },
        ),
        migrations.CreateModel(
            name='CharcoalContract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('entry_date', models.DateField(blank=True, null=True, verbose_name='Data de Entrada')),
                ('contract_volume', models.FloatField(verbose_name='Volume do Contrato (m³)')),
                ('price', models.FloatField(verbose_name='Preço (R$)')),
                ('active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('legal_department_signed', models.BooleanField(default=False, verbose_name='Assinatura do Jurídico')),
                ('supplier_signed', models.BooleanField(default=False, verbose_name='Assinatura do Fornecedor')),
                ('gelf_signed', models.BooleanField(default=False, verbose_name='Assinatura da GELF')),
                ('file', models.FileField(blank=True, null=True, upload_to=gelfmp.models.charcoal_contract.CharcoalContract.upload_to, validators=[gelfmp.utils.validators.validate_max_file_size], verbose_name='Arquivo de Contrato')),
                ('dcf', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='charcoal_contracts', to='gelfmp.dcf', verbose_name='DCF')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='charcoal_contracts', to='gelfmp.supplier', verbose_name='Fornecedor')),
            ],
            options={
                'verbose_name': 'Contrato de Carvão',
                'verbose_name_plural': 'Contratos de Carvão',
            },
        ),
        migrations.CreateModel(
            name='BankDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('bank_name', models.CharField(max_length=255, verbose_name='Banco')),
                ('agency', models.CharField(max_length=10, verbose_name='Agência')),
                ('account_number', models.CharField(max_length=20, verbose_name='Número da Conta')),
                ('account_cnpj', models.CharField(blank=True, max_length=20, null=True, validators=[django.core.validators.RegexValidator(message='Insira um CNPJ válido. Use apenas numeros ou 00.000.000/0000-00.', regex='^(\\w{14}|\\d{2}.\\d{3}.\\d{3}/\\d{4}-\\d{2})$')], verbose_name='CNPJ da Conta')),
                ('bank_code', models.CharField(max_length=5, validators=[django.core.validators.RegexValidator(message='Insira um número válido, usando o formato 000 (3 dígitos).', regex='^\\d{3}')], verbose_name='Número do Banco')),
                ('supplier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bank_details', to='gelfmp.supplier', verbose_name='Fornecedor')),
            ],
            options={
                'verbose_name': 'Detalhes Bancários',
                'verbose_name_plural': 'Detalhes Bancários',
                'ordering': ['bank_name'],
            },
        ),
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('alias', models.CharField(help_text='Nome alternativo que identifica o fornecedor.', max_length=255, unique=True, verbose_name='Alias')),
                ('supplier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='gelfmp.supplier', verbose_name='Fornecedor')),
            ],
            options={
                'verbose_name': 'Alias',
                'verbose_name_plural': 'Aliases',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('description', models.TextField(max_length=255, verbose_name='Descrição')),
                ('due_date', models.DateField(blank=True, null=True, verbose_name='Data de Vencimento')),
                ('status', models.CharField(choices=[('pending', 'Pendente'), ('in_progress', 'Em andamento'), ('completed', 'Completa')], default='pending', max_length=20, verbose_name='Status')),
                ('assigned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks_assigned_by', to=settings.AUTH_USER_MODEL, verbose_name='Atribuído por')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks_assigned_to', to=settings.AUTH_USER_MODEL, verbose_name='Atribuído a')),
                ('completed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks_completed_by', to=settings.AUTH_USER_MODEL, verbose_name='Concluído por')),
            ],
            options={
                'verbose_name': 'Tarefa',
                'verbose_name_plural': 'Tarefas',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['material_type'], name='gelfmp_supp_materia_72a935_idx'),
        ),
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['state'], name='gelfmp_supp_state_i_b538ae_idx'),
        ),
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['cpf_cnpj'], name='gelfmp_supp_cpf_cnp_4b5790_idx'),
        ),
        migrations.AddConstraint(
            model_name='dcf',
            constraint=models.UniqueConstraint(fields=('process_number',), name='dcf_process_number_unique_constraint'),
        ),
        migrations.AddConstraint(
            model_name='charcoalmonthlyplan',
            constraint=models.UniqueConstraint(fields=('supplier', 'month', 'year'), name='charcoal_monthly_plan_supplier_month_year_unique_constraint'),
        ),
        migrations.AddConstraint(
            model_name='charcoaliqf',
            constraint=models.UniqueConstraint(fields=('supplier', 'month', 'year'), name='charcoal_iqf_supplier_month_year_unique_constraint'),
        ),
        migrations.AddIndex(
            model_name='charcoalentry',
            index=models.Index(fields=['entry_date'], name='gelfmp_char_entry_d_506da5_idx'),
        ),
        migrations.AddIndex(
            model_name='charcoalentry',
            index=models.Index(fields=['supplier'], name='gelfmp_char_supplie_c9b051_idx'),
        ),
        migrations.AddIndex(
            model_name='charcoalentry',
            index=models.Index(fields=['dcf'], name='gelfmp_char_dcf_id_19eb73_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['assigned_to'], name='gelfmp_task_assigne_35a9dc_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['due_date'], name='gelfmp_task_due_dat_fefc41_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['status'], name='gelfmp_task_status_14d5d6_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['created_at'], name='gelfmp_task_created_0c62e0_idx'),
        ),
    ]
