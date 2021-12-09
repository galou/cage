# Options for inkscape's generator.py to generated pdf files.
set(PDF_GENERATOR_OPTS --data-file=${DATA_FILE} --var-type=name --extra-vars=${EXTRA_REPLACEMENT} --format=pdf)

# Options for inkscape's generator.py to generated svg files.
set(SVG_GENERATOR_OPTS --data-file=${DATA_FILE} --var-type=name --extra-vars=${EXTRA_REPLACEMENT} --format=svg)

function(generate_calendar)
	# Entry-point to generate the calendar.
	generate_list(pages ${FIRST_GEN_PAGE} ${LAST_GEN_PAGE} 1)

	if(GENERATE_SVG)
		add_inkscape_generator_svg(${page})
		foreach(page IN LISTS pages)
			add_one_generated_pdf_from_svg(${page})
		endforeach()
	else()
		add_inkscape_generator_pdf(${FIRST_GEN_PAGE} ${LAST_GEN_PAGE})
		foreach(page IN LISTS pages)
			add_one_generated_pdf(${page})
		endforeach()
	endif()

	assemble_pdf("${pages}" "${EXTRA_BEFORE}" "${EXTRA_AFTER}")
endfunction()

function(iseven result number)
	# Result 1 if the number is even, 0 otherwise.
	math(EXPR out "${number} % 2")
	if (${out})
		# Odd.
		set(${result} 0 PARENT_SCOPE)
	else()
		# Even.
		set(${result} 1 PARENT_SCOPE)
	endif()
endfunction()

# Return the first even number greater or equal to the given number.
function(first_even result number)
	iseven(res ${number})
	if (${res})
		set(${result} ${number} PARENT_SCOPE)
	else()
		math(EXPR res "${number} + 1")
		set(${result} ${res} PARENT_SCOPE)
	endif()
endfunction()

# Return the first odd number greater or equal to the given number.
function(first_odd result number)
	iseven(res ${number})
	if (${res})
		math(EXPR res "${number} + 1")
		set(${result} ${res} PARENT_SCOPE)
	else()
		set(${result} ${number} PARENT_SCOPE)
	endif()
endfunction()

function(generate_list result_name start end step)
	# Generate a list with optional step from start to end, included.
	if (${ARGC} LESS 4)
		set(step 1)
	endif()
	set(result "")
	foreach(loop_var RANGE ${start} ${end} ${step})
		list(APPEND result ${loop_var})
	endforeach()
	set(${result_name} ${result} PARENT_SCOPE)
endfunction()

function(prepend_zeros number_name length_name result_name)
	# Prepend 0 so that the string is at least length long.
	string(LENGTH ${number_name} length)
	if (${length} GREATER_EQUAL ${length_name})
		# Nothing to be done.
		set(${result_name} ${number_name} PARENT_SCOPE)
	else()
		math(EXPR missing_zero_count "${length_name} - ${length}")
		set(result "${number_name}")
		foreach(loop_var RANGE 1 ${missing_zero_count})
			set(result "0${result}")
		endforeach()
		set(${result_name} ${result} PARENT_SCOPE)
	endif()
endfunction()

function(add_inkscape_generator_pdf first_page last_page)
	# Add the target to build the pdf from inkscape_generator.

	set(PYTHONPATH "${INKEX_PY_DIR}:$ENV{PYTHONPATH}")

	# Even pages (left).
	first_even(first ${first_page})
	generate_list(pages ${first} ${LAST_GEN_PAGE} 2)
	get_generated_file_list(file_list "${pages}" "p" "-gen.pdf")

	set(template ${CMAKE_SOURCE_DIR}/${SVG_EVEN})
	set(pdf_generator_template p%VAR_page_left%-gen.pdf)

	add_custom_command(OUTPUT ${file_list}
		COMMAND ${CMAKE_COMMAND} -E env PYTHONPATH=${PYTHONPATH} python3 ${GENERATOR} ${PDF_GENERATOR_OPTS} --output-pattern=${pdf_generator_template} ${template}
		# BYPRODUCTS file_list
		MAIN_DEPENDENCY ${template} ${DATA_FILE}
		DEPENDS ${template} ${DATA_FILE}
		COMMENT Generating even pages
		VERBATIM
	)

	add_custom_target(generate-pdf-even
		ALL
		DEPENDS ${template} ${DATA_FILE} ${file_list}
	)

	# Odd pages (right).
	first_odd(first ${first_page})
	generate_list(pages ${first} ${LAST_GEN_PAGE} 2)
	get_generated_file_list(file_list "${pages}" "p" "-gen.pdf")

	set(template ${CMAKE_SOURCE_DIR}/${SVG_ODD})
	set(pdf_generator_template p%VAR_page_right%-gen.pdf)

	add_custom_command(OUTPUT ${file_list}
		COMMAND ${CMAKE_COMMAND} -E env PYTHONPATH=${PYTHONPATH} python3 ${GENERATOR} ${PDF_GENERATOR_OPTS} --output-pattern=${pdf_generator_template} ${template}
		# BYPRODUCTS file_list
		MAIN_DEPENDENCY ${template} ${DATA_FILE}
		DEPENDS ${template} ${DATA_FILE}
		COMMENT Generating odd pages
		VERBATIM
	)

	add_custom_target(generate-pdf-odd
		DEPENDS ${template} ${DATA_FILE} ${file_list}
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
	set(svg_generator_template p%VAR_page_left%-gen.svg)

	add_custom_command(OUTPUT ${file_list}
		COMMAND ${CMAKE_COMMAND} -E env PYTHONPATH=${PYTHONPATH} python3 ${GENERATOR} ${SVG_GENERATOR_OPTS} --output-pattern=${svg_generator_template} ${template}
		DEPENDS ${template} ${DATA_FILE}
		COMMENT Generating generate-svg-even
		VERBATIM
	)

	# add_custom_target(generate-svg-even
	# 	ALL
	# 	DEPENDS ${template} generate-svg-even.stamp
	# )

	# Odd pages (right).
	set(template ${CMAKE_SOURCE_DIR}/${SVG_ODD})
	set(svg_generator_template p%VAR_page_right%-gen.svg)

	add_custom_command(OUTPUT ${file_list}
		COMMAND ${CMAKE_COMMAND} -E env PYTHONPATH=${PYTHONPATH} python3 ${GENERATOR} ${SVG_GENERATOR_OPTS} --output-pattern=${svg_generator_template} ${template}
		DEPENDS ${template} ${DATA_FILE}
		COMMENT Generating generate-svg-odd
		VERBATIM
	)

	# add_custom_target(generate-svg-odd
	# 	ALL
	# 	DEPENDS ${template} generate-svg-odd.stamp
	# )

	# All generated svg.
	add_custom_target(generate-svg
		ALL
		DEPENDS generate-svg-even generate-svg-odd
	)
endfunction()

function(add_one_generated_pdf page_name)
	# Add the targets to generate one pdf page directly from template.
	prepend_zeros(${page_name} 3 formatted_page)

	# iseven(res ${page_name})
	# if (${res})
	# 	add_custom_target(generate-pdf-p${formatted_page}
	# 		ALL
	# 		DEPENDS generate-pdf-even.stamp
	# 	)
	# else()
	# 	add_custom_target(generate-pdf-p${formatted_page}
	# 		ALL
	# 		DEPENDS generate-pdf-odd.stamp
	# 	)
	# endif()
endfunction()

function(add_one_generated_pdf_from_svg page_name)
	# Add the targets to generate one pdf page through svg.
	# These targets are not built by default.
	prepend_zeros(${page_name} 3 formatted_page)

	# iseven(res ${page_name})
	# if (${res})
	# 	add_custom_target(generate-pdf-p${formatted_page}-from_svg
	# 		ALL
	# 		DEPENDS generate-svg-even.stamp generate-pdf-p${formatted_page}
	# 	)
	# else()
	# 	add_custom_target(generate-pdf-p${formatted_page}-from_svg
	# 		ALL
	# 		DEPENDS generate-svg-odd.stamp generate-pdf-p${formatted_page}
	# 	)
	# endif()

	add_custom_command(OUTPUT generate-pdf-p${formatted_page}
		COMMAND inkscape --without-gui --file=${CMAKE_BINARY_DIR}/p${formatted_page}-gen.svg --export-pdf=${CMAKE_BINARY_DIR}/p${formatted_page}-gen.pdf
		COMMENT Generating p${formatted_page}.pdf from svg
	)

endfunction()

function(get_generated_file_list result_name pages_name prefix_name suffix_name)
	# Return the list e.g. "p002-gen.pdf;p003-gen.pdf,...".
	# Return the list ${prefix_name}00x${suffix_name} for x in pages_name.
	set(result "")
	foreach(page IN LISTS pages_name)
		prepend_zeros(${page} 3 formatted_page)
		list(APPEND result ${prefix_name}${formatted_page}${suffix_name})
	endforeach()
	set(${result_name} ${result} PARENT_SCOPE)
endfunction()

function(prefix_build_dir output_name input_name)
	set(result "")
	foreach(output IN LISTS input_name)
		list(APPEND result "${CMAKE_BINARY_DIR}/${output}")
	endforeach()
	set(${output_name} ${result} PARENT_SCOPE)
endfunction()

function(assemble_pdf pages_name extra_before_name extra_after_name)
	get_generated_file_list(file_list "${pages_name}" "p" "-gen.pdf")
	string(REPLACE ".pdf" "-single_page.pdf" output_file_single_page ${OUTPUT_FILE})

	prefix_build_dir(eb "${extra_before_name}")
	prefix_build_dir(ea "${extra_after_name}")

	add_custom_command(OUTPUT ${output_file_single_page}
		COMMAND pdfjam --vanilla --rotateoversize false --quiet --outfile "${output_file_single_page}" ${extra_before_name} ${file_list} ${extra_after_name}
		DEPENDS ${eb} ${file_list} ${ea}
	)

	add_custom_command(OUTPUT ${OUTPUT_FILE}
		COMMAND pdfjam --booklet true --landscape --vanilla --rotateoversize false --quiet --outfile "${OUTPUT_FILE}" ${extra_before_name} ${file_list} ${extra_after_name}
		DEPENDS ${eb} ${file_list} ${ea}
	)

	add_custom_target(${OUTPUT_FILE}-single_page
		DEPENDS
		generate-pdf ${output_file_single_page} ${eb} ${file_list} ${ea}
	)

	add_custom_target(${OUTPUT_FILE}-booklet
		ALL
		DEPENDS generate-pdf ${OUTPUT_FILE} ${eb} ${file_list} ${ea}
	)
endfunction()
