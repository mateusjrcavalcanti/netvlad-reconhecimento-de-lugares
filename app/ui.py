import gradio as gr

from database import descriptor_count, descriptor_database_path, descriptors_ready
from datasets import (
    class_names,
    create_class,
    create_dataset,
    dataset_choices_update,
    dataset_gallery,
    dataset_summary,
    datasets_table,
    delete_class,
    delete_dataset,
    delete_image,
    describe_dataset_images,
    extract_frames_from_video,
    image_names,
    list_dataset_names,
    rename_class,
    upload_images,
)
from recognition import recognize_place


def descriptor_summary(dataset_name, last_action="Status atualizado."):
    if not dataset_name:
        return (
            0,
            "Sem dataset",
            0,
            0,
            "",
            "Crie ou selecione um dataset para continuar.",
            last_action,
        )

    count = descriptor_count(dataset_name)
    dataset = dataset_summary(dataset_name)

    if count == 0:
        state = "Pendente"
        next_step = "Gere os descritores do dataset para liberar o reconhecimento."
    else:
        state = "Pronto"
        next_step = "A aba de reconhecimento esta liberada para este dataset."

    return (
        count,
        state,
        dataset["classes"],
        dataset["available_images"],
        str(descriptor_database_path(dataset_name)),
        next_step,
        last_action,
    )


def descriptor_status_with_recognition_visibility(dataset_name):
    ready = descriptors_ready(dataset_name) if dataset_name else False
    return (*descriptor_summary(dataset_name), gr.update(visible=ready))


def describe_dataset_images_with_recognition_visibility(dataset_name, progress=gr.Progress(track_tqdm=False)):
    last_action = describe_dataset_images(dataset_name, progress)
    return (*descriptor_summary(dataset_name, last_action), gr.update(visible=descriptors_ready(dataset_name)))


def refresh_dataset_view(dataset_name, location=None):
    table = datasets_table()
    status, gallery, location_update = dataset_gallery(dataset_name, location)
    return table, status, gallery, location_update


def refresh_gallery_only(dataset_name, location):
    status, gallery, _ = dataset_gallery(dataset_name, location)
    return status, gallery


def refresh_edit_class(dataset_name, class_name):
    status, gallery, _ = dataset_gallery(dataset_name, class_name)
    return status, gallery, image_choices_update(dataset_name, class_name)


def image_choices_update(dataset_name, class_name, selected_image=None):
    names = image_names(dataset_name, class_name)
    value = selected_image if selected_image in names else (names[0] if names else None)
    return gr.update(choices=names, value=value)


def create_dataset_and_refresh(dataset_name):
    try:
        message, dataset_update = create_dataset(dataset_name)
    except Exception as exc:
        message = f"Erro: {exc}"
        dataset_update = dataset_choices_update()

    selected_dataset = dataset_name if dataset_name in list_dataset_names() else None
    table, status, gallery, location_update = refresh_dataset_view(selected_dataset)
    return (
        message,
        dataset_update,
        table,
        status,
        gallery,
        location_update,
    )


def delete_dataset_and_refresh(dataset_name, confirmation):
    if confirmation != dataset_name:
        message = "Digite exatamente o nome do dataset ativo para confirmar a remocao."
        table, status, gallery, location_update = refresh_dataset_view(dataset_name)
        return message, dataset_choices_update(dataset_name), table, status, gallery, location_update, gr.update()

    try:
        message, dataset_update = delete_dataset(dataset_name)
    except Exception as exc:
        message = f"Erro: {exc}"
        dataset_update = dataset_choices_update(dataset_name)

    selected_dataset = dataset_update.get("value") if isinstance(dataset_update, dict) else None
    table, status, gallery, location_update = refresh_dataset_view(selected_dataset)
    return message, dataset_update, table, status, gallery, location_update, image_choices_update(selected_dataset, None)


def create_class_and_refresh(dataset_name, class_name):
    try:
        message = create_class(dataset_name, class_name)
    except Exception as exc:
        message = f"Erro: {exc}"

    table, status, gallery, location_update = refresh_dataset_view(dataset_name, class_name)
    return message, table, status, gallery, location_update, location_update, image_choices_update(dataset_name, class_name)


def upload_images_and_refresh(dataset_name, class_name, files):
    try:
        message = upload_images(dataset_name, class_name, files)
    except Exception as exc:
        message = f"Erro: {exc}"

    table, status, gallery, location_update = refresh_dataset_view(dataset_name, class_name)
    return message, table, status, gallery, location_update, image_choices_update(dataset_name, class_name)


def rename_class_and_refresh(dataset_name, class_name, new_class_name):
    try:
        message = rename_class(dataset_name, class_name, new_class_name)
        selected_class = new_class_name
    except Exception as exc:
        message = f"Erro: {exc}"
        selected_class = class_name

    table, status, gallery, location_update = refresh_dataset_view(dataset_name, selected_class)
    return message, table, status, gallery, location_update, location_update, image_choices_update(dataset_name, selected_class)


def delete_class_and_refresh(dataset_name, class_name, confirmation):
    if confirmation != class_name:
        message = "Digite exatamente o nome da classe ativa para confirmar a remocao."
        table, status, gallery, location_update = refresh_dataset_view(dataset_name, class_name)
        return message, table, status, gallery, location_update, location_update, image_choices_update(dataset_name, class_name)

    try:
        message = delete_class(dataset_name, class_name)
    except Exception as exc:
        message = f"Erro: {exc}"

    table, status, gallery, location_update = refresh_dataset_view(dataset_name)
    return message, table, status, gallery, location_update, location_update, image_choices_update(dataset_name, None)


def delete_image_and_refresh(dataset_name, class_name, image_name, confirmation):
    if confirmation != image_name:
        message = "Digite exatamente o nome da imagem ativa para confirmar a remocao."
        table, status, gallery, location_update = refresh_dataset_view(dataset_name, class_name)
        return message, table, status, gallery, location_update, image_choices_update(dataset_name, class_name, image_name)

    try:
        message = delete_image(dataset_name, class_name, image_name)
    except Exception as exc:
        message = f"Erro: {exc}"

    table, status, gallery, location_update = refresh_dataset_view(dataset_name, class_name)
    return message, table, status, gallery, location_update, image_choices_update(dataset_name, class_name)


def extract_video_frames_and_refresh(dataset_name, video_path, fps, intervals, progress=gr.Progress()):
    try:
        message, extracted_images = extract_frames_from_video(dataset_name, video_path, fps, intervals, progress)
    except Exception as exc:
        message = f"Erro: {exc}"
        extracted_images = []

    table, status, gallery, location_update = refresh_dataset_view(dataset_name)
    return message, extracted_images, table, status, gallery, location_update, location_update


def update_all_for_dataset(dataset_name):
    table, status, gallery, location_update = refresh_dataset_view(dataset_name)
    descriptor_values = descriptor_status_with_recognition_visibility(dataset_name)
    return (
        table,
        status,
        gallery,
        location_update,
        location_update,
        image_choices_update(dataset_name, location_update.get("value") if isinstance(location_update, dict) else None),
        *descriptor_values,
    )


def show_edit_mode(dataset_name):
    if not dataset_name:
        return gr.update(visible=False), gr.update(choices=[], value=None), "Selecione um dataset para editar."

    names = class_names(dataset_name)
    value = names[0] if names else None
    return gr.update(visible=True), gr.update(choices=names, value=value), f"Editando dataset {dataset_name}."


def hide_edit_mode():
    return gr.update(visible=False), ""


def build_interface():
    dataset_names = list_dataset_names()
    initial_dataset = dataset_names[0] if dataset_names else None

    with gr.Blocks(title="NetVLAD VPR") as demo:
        gr.Markdown("# NetVLAD VPR")
        gr.Markdown("Reconhecimento visual de lugares usando descritores NetVLAD.")

        with gr.Tab("1. Datasets"):
            dataset_action = gr.Textbox(label="Última ação", interactive=False)

            with gr.Tab("Ver datasets"):
                with gr.Row():
                    dataset_selector = gr.Dropdown(
                        dataset_names,
                        label="Dataset ativo",
                        value=initial_dataset,
                    )
                    edit_dataset_mode_button = gr.Button("Editar dataset", variant="primary")

                datasets_grid = gr.Dataframe(
                    headers=["Dataset", "Classes", "Imagens", "Banco"],
                    label="Datasets disponíveis",
                    interactive=False,
                )
                class_selector = gr.Dropdown(
                    [],
                    label="Classe/local",
                )
                dataset_status = gr.Markdown()
                gallery = gr.Gallery(
                    label="Imagens do dataset",
                    columns=8,
                    object_fit="cover",
                )

                with gr.Group(visible=False) as edit_dataset_group:
                    active_edit_class = gr.Dropdown([], label="Classe ativa")

                    with gr.Tab("Classes"):
                        new_class_name = gr.Textbox(label="Nova classe")
                        create_class_button = gr.Button("Criar nova classe", variant="primary")
                        renamed_class_name = gr.Textbox(label="Novo nome da classe ativa")
                        rename_class_button = gr.Button("Renomear classe ativa")
                        delete_class_confirmation = gr.Textbox(label="Confirmar remoção da classe ativa")
                        delete_class_button = gr.Button("Remover classe ativa", variant="stop")

                    with gr.Tab("Imagens"):
                        active_image = gr.Dropdown([], label="Imagem ativa")
                        image_files = gr.File(
                            label="Adicionar imagens a classe ativa",
                            file_count="multiple",
                            type="filepath",
                        )
                        upload_button = gr.Button("Enviar imagens", variant="primary")
                        delete_image_confirmation = gr.Textbox(label="Confirmar remoção da imagem ativa")
                        delete_image_button = gr.Button("Remover imagem ativa", variant="stop")

                    with gr.Tab("Vídeo"):
                        video_file = gr.Video(label="Vídeo")
                        video_fps = gr.Number(label="Frames por segundo", value=1, precision=2)
                        video_intervals = gr.Dataframe(
                            headers=["Início (s)", "Fim (s)", "Classe"],
                            value=[[0, 5, ""]],
                            row_count=(1, "dynamic"),
                            col_count=(3, "fixed"),
                            label="Intervalos de extração",
                            interactive=True,
                        )
                        extract_video_button = gr.Button("Extrair frames para o dataset", variant="primary")
                        extracted_frames_gallery = gr.Gallery(
                            label="Frames extraídos",
                            columns=8,
                            object_fit="cover",
                        )

                    with gr.Tab("Dataset"):
                        delete_dataset_confirmation = gr.Textbox(label="Confirmar remoção do dataset ativo")
                        delete_dataset_button = gr.Button("Remover dataset ativo", variant="stop")

                    with gr.Row():
                        finish_edit_button = gr.Button("Concluir edição")

            with gr.Tab("Novo dataset"):
                new_dataset_name = gr.Textbox(label="Novo dataset")
                create_dataset_button = gr.Button("Criar dataset", variant="primary")

        with gr.Tab("2. Preparar descritores"):
            with gr.Row():
                with gr.Group():
                    descriptor_total = gr.Number(label="Descritores", precision=0, interactive=False)
                    descriptor_state = gr.Textbox(label="Estado", interactive=False)
                with gr.Group():
                    class_count = gr.Number(label="Classes", precision=0, interactive=False)
                    available_images = gr.Number(label="Imagens disponíveis", precision=0, interactive=False)
                with gr.Group():
                    database_path = gr.Textbox(label="Banco SQLite", interactive=False)
                    next_step = gr.Textbox(label="Próximo passo", interactive=False)

            last_action = gr.Textbox(label="Última ação", lines=2, interactive=False)
            refresh_button = gr.Button("Atualizar status")
            generate_button = gr.Button("Gerar descritores do dataset ativo", variant="primary")

        with gr.Tab(
            "3. Reconhecer lugar",
            visible=descriptors_ready(initial_dataset) if initial_dataset else False,
        ) as recognize_tab:
            with gr.Row():
                input_image = gr.Image(type="filepath", label="Imagem de consulta")
                with gr.Column():
                    recognize_button = gr.Button("Reconhecer", variant="primary")
                    result = gr.Textbox(label="Resultado", lines=4)
                    saved_image = gr.Textbox(label="Imagem de consulta salva", interactive=False)

            reference_image = gr.Image(type="filepath", label="Imagem de referência mais próxima")
            top_matches = gr.Dataframe(
                headers=["Classe", "Imagem", "Distancia"],
                label="Top matches",
                interactive=False,
            )
            recognize_button.click(
                recognize_place,
                inputs=[dataset_selector, input_image],
                outputs=[result, saved_image, reference_image, top_matches],
            )

        edit_dataset_mode_button.click(
            show_edit_mode,
            inputs=dataset_selector,
            outputs=[edit_dataset_group, active_edit_class, dataset_action],
        )
        finish_edit_button.click(
            hide_edit_mode,
            outputs=[edit_dataset_group, dataset_action],
        )
        dataset_selector.change(
            update_all_for_dataset,
            inputs=dataset_selector,
            outputs=[
                datasets_grid,
                dataset_status,
                gallery,
                class_selector,
                active_edit_class,
                active_image,
                descriptor_total,
                descriptor_state,
                class_count,
                available_images,
                database_path,
                next_step,
                last_action,
                recognize_tab,
            ],
        )
        class_selector.change(
            refresh_gallery_only,
            inputs=[dataset_selector, class_selector],
            outputs=[dataset_status, gallery],
        )
        active_edit_class.change(
            refresh_edit_class,
            inputs=[dataset_selector, active_edit_class],
            outputs=[dataset_status, gallery, active_image],
        )
        create_dataset_button.click(
            create_dataset_and_refresh,
            inputs=new_dataset_name,
            outputs=[
                dataset_action,
                dataset_selector,
                datasets_grid,
                dataset_status,
                gallery,
                class_selector,
            ],
        )
        create_class_button.click(
            create_class_and_refresh,
            inputs=[dataset_selector, new_class_name],
            outputs=[dataset_action, datasets_grid, dataset_status, gallery, class_selector, active_edit_class, active_image],
        )
        rename_class_button.click(
            rename_class_and_refresh,
            inputs=[dataset_selector, active_edit_class, renamed_class_name],
            outputs=[dataset_action, datasets_grid, dataset_status, gallery, class_selector, active_edit_class, active_image],
        )
        delete_class_button.click(
            delete_class_and_refresh,
            inputs=[dataset_selector, active_edit_class, delete_class_confirmation],
            outputs=[dataset_action, datasets_grid, dataset_status, gallery, class_selector, active_edit_class, active_image],
        )
        upload_button.click(
            upload_images_and_refresh,
            inputs=[dataset_selector, active_edit_class, image_files],
            outputs=[dataset_action, datasets_grid, dataset_status, gallery, class_selector, active_image],
        )
        delete_image_button.click(
            delete_image_and_refresh,
            inputs=[dataset_selector, active_edit_class, active_image, delete_image_confirmation],
            outputs=[dataset_action, datasets_grid, dataset_status, gallery, class_selector, active_image],
        )
        extract_video_button.click(
            extract_video_frames_and_refresh,
            inputs=[dataset_selector, video_file, video_fps, video_intervals],
            outputs=[
                dataset_action,
                extracted_frames_gallery,
                datasets_grid,
                dataset_status,
                gallery,
                class_selector,
                active_edit_class,
            ],
            show_progress_on=[dataset_action],
        )
        delete_dataset_button.click(
            delete_dataset_and_refresh,
            inputs=[dataset_selector, delete_dataset_confirmation],
            outputs=[dataset_action, dataset_selector, datasets_grid, dataset_status, gallery, class_selector, active_image],
        )
        refresh_button.click(
            descriptor_status_with_recognition_visibility,
            inputs=dataset_selector,
            outputs=[
                descriptor_total,
                descriptor_state,
                class_count,
                available_images,
                database_path,
                next_step,
                last_action,
                recognize_tab,
            ],
            show_progress_on=[last_action],
        )
        generate_button.click(
            describe_dataset_images_with_recognition_visibility,
            inputs=dataset_selector,
            outputs=[
                descriptor_total,
                descriptor_state,
                class_count,
                available_images,
                database_path,
                next_step,
                last_action,
                recognize_tab,
            ],
            show_progress_on=[last_action],
        )
        demo.load(
            update_all_for_dataset,
            inputs=dataset_selector,
            outputs=[
                datasets_grid,
                dataset_status,
                gallery,
                class_selector,
                active_edit_class,
                active_image,
                descriptor_total,
                descriptor_state,
                class_count,
                available_images,
                database_path,
                next_step,
                last_action,
                recognize_tab,
            ],
            show_progress_on=[last_action],
        )

    return demo
