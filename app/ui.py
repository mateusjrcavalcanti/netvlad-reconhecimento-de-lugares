import gradio as gr

from config import DATABASE_PATH
from database import descriptor_count, descriptors_ready
from datasets import dataset_gallery, dataset_summary, describe_dataset_images, load_locations
from recognition import recognize_place


def descriptor_summary(last_action="Status atualizado."):
    count = descriptor_count()
    dataset = dataset_summary()

    if count == 0:
        state = "Pendente"
        next_step = "Gere os descritores do dataset para liberar o reconhecimento."
    else:
        state = "Pronto"
        next_step = "A aba de reconhecimento esta liberada."

    return (
        count,
        state,
        dataset["csv_rows"],
        dataset["available_images"],
        dataset["missing_images"],
        str(DATABASE_PATH),
        next_step,
        last_action,
    )


def descriptor_status_with_recognition_visibility():
    return (*descriptor_summary(), gr.update(visible=descriptors_ready()))


def describe_dataset_images_with_recognition_visibility(progress=gr.Progress(track_tqdm=True)):
    last_action = describe_dataset_images(progress)
    return (*descriptor_summary(last_action), gr.update(visible=descriptors_ready()))


def build_interface():
    locations = sorted(load_locations().keys())

    with gr.Blocks(title="NetVLAD VPR") as demo:
        gr.Markdown("# NetVLAD VPR")
        gr.Markdown("Reconhecimento visual de lugares usando descritores NetVLAD.")

        with gr.Tab("1. Dataset"):
            location = gr.Dropdown(locations, label="Classe/local", value=locations[0] if locations else None)
            dataset_status = gr.Markdown()
            gallery = gr.Gallery(
                label="Imagens do dataset",
                columns=8,
                object_fit="cover",
            )
            location.change(dataset_gallery, inputs=location, outputs=[dataset_status, gallery])
            demo.load(dataset_gallery, inputs=location, outputs=[dataset_status, gallery])

        with gr.Tab("2. Preparar descritores"):
            with gr.Row():
                with gr.Group():
                    descriptor_total = gr.Number(label="Descritores", precision=0, interactive=False)
                    descriptor_state = gr.Textbox(label="Estado", interactive=False)
                with gr.Group():
                    csv_rows = gr.Number(label="Linhas no CSV", precision=0, interactive=False)
                    available_images = gr.Number(label="Imagens disponíveis", precision=0, interactive=False)
                    missing_images = gr.Number(label="Imagens ausentes", precision=0, interactive=False)
                with gr.Group():
                    database_path = gr.Textbox(label="Banco SQLite", interactive=False)
                    next_step = gr.Textbox(label="Próximo passo", interactive=False)

            last_action = gr.Textbox(label="Última ação", lines=2, interactive=False)
            refresh_button = gr.Button("Atualizar status")
            generate_button = gr.Button("Gerar descritores do dataset", variant="primary")

        with gr.Tab("3. Reconhecer lugar", visible=descriptors_ready()) as recognize_tab:
            with gr.Row():
                input_image = gr.Image(type="filepath", label="Imagem de consulta")
                with gr.Column():
                    recognize_button = gr.Button("Reconhecer", variant="primary")
                    result = gr.Textbox(label="Resultado", lines=4)
                    saved_image = gr.Textbox(label="Imagem salva", interactive=False)

            top_matches = gr.Dataframe(
                headers=["Classe", "Distancia"],
                label="Top matches",
                interactive=False,
            )
            recognize_button.click(
                recognize_place,
                inputs=input_image,
                outputs=[result, saved_image, top_matches],
            )

        refresh_button.click(
            descriptor_status_with_recognition_visibility,
            outputs=[
                descriptor_total,
                descriptor_state,
                csv_rows,
                available_images,
                missing_images,
                database_path,
                next_step,
                last_action,
                recognize_tab,
            ],
            show_progress_on=[last_action],
        )
        generate_button.click(
            describe_dataset_images_with_recognition_visibility,
            outputs=[
                descriptor_total,
                descriptor_state,
                csv_rows,
                available_images,
                missing_images,
                database_path,
                next_step,
                last_action,
                recognize_tab,
            ],
            show_progress_on=[last_action],
        )
        demo.load(
            descriptor_status_with_recognition_visibility,
            outputs=[
                descriptor_total,
                descriptor_state,
                csv_rows,
                available_images,
                missing_images,
                database_path,
                next_step,
                last_action,
                recognize_tab,
            ],
            show_progress_on=[last_action],
        )

    return demo
