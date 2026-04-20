#let title-page(
  name: "Student Name",
  reg_no: "0000-XX-000",
  supervisor_name: "Supervisor Name",
  course_name: "Course Name",
  title: "Lab Title",
  doc,
) = {
  set page(
    width: 210mm,
    height: 297mm,
    margin: 2cm,
  )

  set text(
    font: "Times New Roman",
    size: 12pt,
  )

  align(center)[
    #text(size: 22pt, weight: "bold")[#title]

    #v(0.5cm)

    #image("./logo.png", width: 4cm)

    #v(1cm)

    #text(size: 16pt, weight: "bold")[Session 2023 - 2027]

    #v(1.08cm)

    #text(size: 16pt, weight: "bold")[Submitted by:]

    #v(0.5cm)

    #text(size: 16pt)[#name #h(1cm) #reg_no]

    #v(1.08cm)

    #text(size: 16pt, weight: "bold")[Supervised by:]

    #v(0.5cm)

    #text(size: 16pt)[#supervisor_name]

    #v(1.08cm)

    #text(size: 16pt, weight: "bold")[Course:]

    #v(0.5cm)

    #text(size: 16pt)[#course_name]

    #v(1.08cm)

    #text(size: 16pt)[Department of Computer Science]

    #v(0.5cm)

    #text(size: 18pt, weight: "bold")[University of Engineering and Technology]

    #text(size: 18pt, weight: "bold")[Lahore Pakistan]

    #v(2cm)

  ]

  doc
}
