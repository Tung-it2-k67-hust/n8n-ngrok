from reportlab.pdfgen import canvas

def create_pdf(path):
    c = canvas.Canvas(path)
    c.drawString(100, 750, "Hello Gemini!")
    c.drawString(100, 730, "This is a test PDF document.")
    c.drawString(100, 710, "Lesson 1: Introduction")
    c.drawString(100, 690, "System.out.println('Hello World');")
    c.save()

if __name__ == "__main__":
    create_pdf(r"E:\n8n-ngrok\n8n_test\test_sample.pdf")
    print("Created test_sample.pdf")
