process HELLO {
    output:
        path "hello.txt"

    """
    echo "Hello Nextflow!" > hello.txt
    """
}

process UPPERCASE {
    input:
        path input_file
    output:
        path "upper.txt"

    """
    tr '[:lower:]' '[:upper:]' < ${input_file} > upper.txt
    """
}

workflow {
    main:
        hello_out = HELLO()
        UPPERCASE(hello_out)
}
