# Options for inkscape's generator.py to generated pdf files.
set(PDF_GENERATOR_OPTS --data-file=${CMAKE_SOURCE_DIR}/${DATA_FILE} --var-type=name --extra-vars=${EXTRA_REPLACEMENT} --format=pdf)

# Options for inkscape's generator.py to generated svg files.
set(SVG_GENERATOR_OPTS --data-file=${CMAKE_SOURCE_DIR}/${DATA_FILE} --var-type=name --extra-vars=${EXTRA_REPLACEMENT} --format=svg)

# PDFJOIN_CMD must point to pdfjoin of the pdfjam package.
set(PDFJOIN_CMD pdfjoin)

# PDFBOOK_CMD must point to the pdfbook command of the pdfjam package.
set(PDFBOOK_CMD pdfbook)

function(generate_calendar)
	# Entry-point to generate the calendar.
	generate_list_step1(${FIRST_GEN_PAGE} ${LAST_GEN_PAGE} pages)

	if(GENERATE_SVG)
		add_inkscape_generator_svg()
		foreach(page IN LISTS pages)
			add_one_generated_pdf_from_svg(${page})
		endforeach()
	else()
		add_inkscape_generator_pdf()
		foreach(page IN LISTS pages)
			add_one_generated_pdf(${page})
		endforeach()
	endif()

	assemble_pdf("${pages}" "${EXTRA_BEFORE}" "${EXTRA_AFTER}")
endfunction()

function(iseven number_name result_name)
	# Result 1 if the number is even, 0 otherwise.
	math(EXPR out "${number_name} % 2")
	if (${out})
		# Odd.
		set(${result_name} 0 PARENT_SCOPE)
	else()
		# Even.
		set(${result_name} 1 PARENT_SCOPE)
	endif()
endfunction()

function(generate_page_list_even first_page_name last_page_name result_name)
	# Generate a list of even numbers between first_page and last_page.
	iseven(${first_page_name} res)
	math(EXPR start "${first_page_name} - ${res} + 1")
	generate_list_step2(${start} ${last_page_name} ${result_name})
	set(${result_name} ${${result_name}} PARENT_SCOPE)
endfunction()

function(generate_page_list_odd first_page_name last_page_name result_name)
	# Generate a list of odd numbers between first_page and last_page.
	iseven(${first_page_name} res)
	math(EXPR start "${first_page_name} + ${res}")
	generate_list_step2(${start} ${last_page_name} ${result_name})
	set(${result_name} ${${result_name}} PARENT_SCOPE)
endfunction()

function(generate_list_step1 start end result_name)
	# Generate a list with step 1.
	set(${result_name} "")
	foreach(loop_var RANGE ${start} ${end})
		list(APPEND ${result_name} ${loop_var})
	endforeach()
	set(${result_name} ${${result_name}} PARENT_SCOPE)
endfunction()

function(generate_list_step2 start end result_name)
	# Generate a list with step 2.
	set(${result_name} "")
	foreach(loop_var RANGE ${start} ${end} 2)
		list(APPEND ${result_name} ${loop_var})
	endforeach()
	set(${result_name} ${${result_name}} PARENT_SCOPE)
endfunction()

function(prepend_zeros number_name length_name result_name)
	# Prepend 0 so that the string is at least length long.
	string(LENGTH ${number_name} length)
	if (${length} GREATER ${length_name} OR ${length} EQUAL ${length_name})
		# Nothing to be done.
		set(${result_name} ${number_name} PARENT_SCOPE)
	else()
		math(EXPR missing_zero_count "${length_name} - ${length}")
		set(${result_name} "${number_name}")
		foreach(loop_var RANGE 1 ${missing_zero_count})
			set(${result_name} "0${${result_name}}")
		endforeach()
		set(${result_name} ${${result_name}} PARENT_SCOPE)
	endif()
endfunction()

function(add_inkscape_generator_pdf)
	# Add the target to build the pdf from inkscape_generator.

	set(PYTHONPATH "${INKEX_PY_DIR}:$ENV{PYTHONPATH}")

	# Even pages (left).
	set(template ${CMAKE_SOURCE_DIR}/${SVG_EVEN})
	set(pdf_generator_template ${CMAKE_BINARY_DIR}/p%VAR_page_left%-gen.pdf)

	add_custom_command(OUTPUT generate-pdf-even.stamp
		# Portable version with "-E env" available on cmake 3.2.
		# COMMAND ${CMAKE_COMMAND} -E env PYTHONPATH=${PYTHONPATH} ${GENERATOR} ${PDF_GENERATOR_OPTS} --output='${CMAKE_BUILD_DIR}/${generated_svg}' ${template} 1>/dev/null
		COMMAND PYTHONPATH=${PYTHONPATH} python2 ${GENERATOR} ${PDF_GENERATOR_OPTS} --output=${pdf_generator_template} ${template}
		COMMAND ${CMAKE_COMMAND} -E touch generate-pdf-even.stamp
		DEPENDS ${template}
		VERBATIM
	)

	add_custom_target(generate-pdf-even
		ALL
		DEPENDS ${template} ${generated_pdf}
	)

	# Odd pages (right).
	set(template ${CMAKE_SOURCE_DIR}/${SVG_ODD})
	set(pdf_generator_template ${CMAKE_BINARY_DIR}/p%VAR_page_right%-gen.pdf)

	add_custom_command(OUTPUT generate-pdf-odd.stamp
		# Portable version with "-E env" available on cmake 3.2.
		# COMMAND ${CMAKE_COMMAND} -E env PYTHONPATH=${PYTHONPATH} ${GENERATOR} ${PDF_GENERATOR_OPTS} --output='${CMAKE_BUILD_DIR}/${generated_svg}' ${template} 1>/dev/null
		COMMAND PYTHONPATH=${PYTHONPATH} python2 ${GENERATOR} ${PDF_GENERATOR_OPTS} --output=${pdf_generator_template} ${template}
		COMMAND ${CMAKE_COMMAND} -E touch generate-pdf-odd.stamp
		DEPENDS ${template}
		VERBATIM
	)

	add_custom_target(generate-pdf-odd
		DEPENDS ${template} ${generated_pdf}
	)

	# All generated pdf.
	add_custom_target(generate-pdf
		DEPENDS generate-pdf-even generate-pdf-odd
	)

endfunction()

function(add_inkscape_generator_svg)
	# Add the target to build the svg from inkscape_generator. This target is not built by default.

	set(PYTHONPATH "${INKEX_PY_DIR}:$ENV{PYTHONPATH}")

	# Even pages (left).
	set(template ${CMAKE_SOURCE_DIR}/${SVG_EVEN})
	set(svg_generator_template ${CMAKE_BINARY_DIR}/p%VAR_page_left%-gen.svg)

	add_custom_command(OUTPUT generate-svg-even.stamp
		# Portable version with "-E env" available on cmake 3.2.
		# COMMAND ${CMAKE_COMMAND} -E env PYTHONPATH=${PYTHONPATH} ${GENERATOR} ${SVG_GENERATOR_OPTS} --output='${CMAKE_BUILD_DIR}/${generated_svg}' ${template} 1>/dev/null
		COMMAND PYTHONPATH=${PYTHONPATH} python2 ${GENERATOR} ${SVG_GENERATOR_OPTS} --output=${svg_generator_template} ${template}
		COMMAND ${CMAKE_COMMAND} -E touch generate-svg-even.stamp
		DEPENDS ${template}
		COMMENT Generating generate-svg-even
		VERBATIM
	)

	add_custom_target(generate-svg-even
		ALL
		DEPENDS ${template} generate-svg-even.stamp
	)

	# Odd pages (right).
	set(template ${CMAKE_SOURCE_DIR}/${SVG_ODD})
	set(svg_generator_template ${CMAKE_BINARY_DIR}/p%VAR_page_right%-gen.svg)

	add_custom_command(OUTPUT generate-svg-odd.stamp
		# Portable version with "-E env" available on cmake 3.2.
		# COMMAND ${CMAKE_COMMAND} -E env PYTHONPATH=${PYTHONPATH} ${GENERATOR} ${SVG_GENERATOR_OPTS} --output='${CMAKE_BUILD_DIR}/${generated_svg}' ${template} 1>/dev/null
		COMMAND PYTHONPATH=${PYTHONPATH} python2 ${GENERATOR} ${SVG_GENERATOR_OPTS} --output=${svg_generator_template} ${template}
		COMMAND ${CMAKE_COMMAND} -E touch generate-svg-odd.stamp
		DEPENDS ${template}
		COMMENT Generating generate-svg-odd
		VERBATIM
	)

	add_custom_target(generate-svg-odd
		ALL
		DEPENDS ${template} generate-svg-odd.stamp
	)

	# All generated svg.
	add_custom_target(generate-svg
		ALL
		DEPENDS generate-svg-even generate-svg-odd
	)
endfunction()

function(add_one_generated_pdf page_name)
	# Add the targets to generate one pdf page directly from template.
	prepend_zeros(${page_name} 3 formatted_page)

	iseven(${page_name} res)
	if (${res})
		add_custom_target(generate-pdf-p${formatted_page}
			ALL
			DEPENDS generate-pdf-even.stamp
		)
	else()
		add_custom_target(generate-pdf-p${formatted_page}
			ALL
			DEPENDS generate-pdf-odd.stamp
		)
	endif()
endfunction()

function(add_one_generated_pdf_from_svg page_name)
	# Add the targets to generate one pdf page through svg.
	# These targets are not built by default.
	prepend_zeros(${page_name} 3 formatted_page)

	iseven(${page_name} res)
	if (${res})
		add_custom_target(generate-pdf-p${formatted_page}-from_svg
			ALL
			DEPENDS generate-svg-even.stamp generate-pdf-p${formatted_page}
		)
	else()
		add_custom_target(generate-pdf-p${formatted_page}-from_svg
			ALL
			DEPENDS generate-svg-odd.stamp generate-pdf-p${formatted_page}
		)
	endif()

	add_custom_command(OUTPUT generate-pdf-p${formatted_page}
		COMMAND inkscape --without-gui --file=${CMAKE_BINARY_DIR}/p${formatted_page}-gen.svg --export-pdf=${CMAKE_BINARY_DIR}/p${formatted_page}-gen.pdf
		COMMENT Generating p${formatted_page}.pdf from svg
	)
		
endfunction()

function(get_generated_file_list pages_name prefix_name suffix_name result_name)
	set(result "")
	foreach(page IN LISTS pages_name)
		prepend_zeros(${page} 3 formatted_page)
		list(APPEND result ${prefix_name}${formatted_page}${suffix_name})
	endforeach()
	set(${result_name} ${result} PARENT_SCOPE)
endfunction()

function(string_join list_name separator_name result_name)
	set(result "")
	foreach(element IN LISTS list_name)
		set(result "${result} ${element}")
	endforeach()
	set(${result_name} ${result} PARENT_SCOPE)
endfunction()

function(assemble_pdf pages_name extra_before_name extra_after_name)
	get_generated_file_list("${pages_name}" "p" "-gen.pdf" file_list)
	string(REPLACE ".pdf" "-single_page.pdf" output_file_single_page ${OUTPUT_FILE})

	add_custom_command(OUTPUT ${output_file_single_page}
		COMMAND ${PDFJOIN_CMD} --vanilla --rotateoversize false --quiet --outfile "${output_file_single_page}" ${extra_before_name} ${file_list} ${extra_after_name}
	)

	add_custom_command(OUTPUT ${OUTPUT_FILE}
		COMMAND ${PDFBOOK_CMD} --vanilla --rotateoversize false --quiet --outfile "${OUTPUT_FILE}" ${extra_before_name} ${file_list} ${extra_after_name}
	)

	add_custom_target(${OUTPUT_FILE}-single_page
		DEPENDS generate-pdf ${output_file_single_page} ${file_list}
	)

	add_custom_target(${OUTPUT_FILE}-booklet
		ALL
		DEPENDS generate-pdf ${OUTPUT_FILE} ${file_list}
	)
endfunction()

