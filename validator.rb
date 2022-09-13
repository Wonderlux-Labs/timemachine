require 'pry'
directories = Dir["./dance_parties/**"]
directories.each do |dir|
  missing = []
  dance_file = File.join(dir, "audio.mp3")
  missing << dance_file unless File.exist?(dance_file)
  vid1_file = File.join(dir, "vid1.mp4")
  missing << vid1_file unless File.exist?(vid1_file)
  vid2_file = File.join(dir, "vid2.mp4")
  missing << vid2_file unless File.exist?(vid2_file)
  intro_file = File.join(dir, "intro.txt")
  missing << intro_file unless File.exist?(intro_file)
  if missing.empty?
    puts "#{dir} is valid"
  else
    puts "#{dir} is missing #{missing.join(', ')}"
  end
  puts '---'
end
puts "#{directories.count} dance parties"
