"""Test public methods for `readBackwards.BackwardsReader`"""

from FoGSE.readBackwards import BackwardsReader

def _run_readline(fn, bs):
        """Open a file with a buffer-size and return the output of the `readline` method 
        for all lines in the buffer."""
        # read file backwards now
        lines_read_backwards = []
        with BackwardsReader(file=fn, blksize=bs) as f:
            line = f.readline()
            # if no line to be read then line == ""
            while line:
                # print("backwards ",line==b'4.800000000000000000e+01 9.078270311320314478e-01\n', len(line.decode('utf-8')))
                lines_read_backwards.append(line)
                line = f.readline()
        return lines_read_backwards

def _run_readlines(fn, bs):
        """Open a file with a buffer-size and return the output of the `readlines` method."""
        # read file backwards now
        with BackwardsReader(file=fn, blksize=bs) as f:
            lines = f.readlines()
        return lines

def _run_read_block(fn, bs):
        """Open a file with a buffer-size and return the output of the `read_block` method."""
        # read file backwards now
        with BackwardsReader(file=fn, blksize=bs) as f:
            lines = f.read_block()
        return lines

def _one_to_ones_match(list1,list2_s,identity):
     """Check for a one-to-one match between two lists."""
     assert len(list1)==len(list2_s), f"Line lists do not match ({identity})."
     for l1,l2 in zip(list1,list2_s):
          assert l1==l2+b'\n', f"Line lists do not match ({identity})."

def _check_block_match(manual,block,identity):
     """Check the creation of he block matches the block.
     
     This may need a b'\n' added."""
     # original and original with b'\n' removed from end
     manual0 = [manual, manual[:-1]]
     # may need b'\n'
     manual1 = [b'\n'+manual, b'\n'+manual+b'\n', manual+b'\n']
     # manual may/should also have b'\n' at the end
     manual2 = [b'\n'+manual[:-1], b'\n'+manual[:-1]+b'\n', manual[:-1]+b'\n']
     assert block in manual0+manual1+manual2, f"Blocks do not match ({identity})."

def test_readline():
    """Testing the readline method in `readBackwards.BackwardsReader`."""
    filename0 = "./test_data/test_file0.txt" # bunch of numbers
    filename1 = "./test_data/test_file1.txt" # same as filename0 but with blank line at the end
    filename2 = "./test_data/test_file2.txt" # completely empty file

    first_infile0 = [b'0.000000000000000000e+00 7.552998431438581184e-01\n',
                     b'1.000000000000000000e+00 8.836227210781278929e-01\n',
                     b'2.000000000000000000e+00 3.814462248357055607e-01\n',
                     b'3.000000000000000000e+00 4.812185877057306715e-01\n',
                     b'4.000000000000000000e+00 9.084281373723649411e-01\n']
    last_infile0 = [b'4.400000000000000000e+01 6.534142139052050435e-01\n',
                    b'4.500000000000000000e+01 7.841096851532141088e-01\n',
                    b'4.600000000000000000e+01 3.413022875063899120e-01\n',
                    b'4.700000000000000000e+01 1.182035700537523715e-01\n',
                    b'4.800000000000000000e+01 9.078270311320314478e-01\n']
    
    # buffer sizes
    buffsize0 = 1000 # in Bytes, 1000 is loads to make sure we get the last 5 lines
    buffsize1 = 4096 # in Bytes, this is loads more than the file, should contain all lines
    buffsize2 = 0 # in Bytes, this should contain all lines
    buffsize3 = -1 # in Bytes, this should contain all lines

    # read file backwards now, filename0
    lines_read_backwards00 = _run_readline(fn=filename0, bs=buffsize0)
    lines_read_backwards01 = _run_readline(fn=filename0, bs=buffsize1)
    lines_read_backwards02 = _run_readline(fn=filename0, bs=buffsize2)
    lines_read_backwards03 = _run_readline(fn=filename0, bs=buffsize3)
    # test against the manually copied lines
    _len_checks = len(last_infile0)
    for i in range(_len_checks):
        assert lines_read_backwards00[i]==last_infile0[_len_checks-(i+1)], "Last lines in {filename0} do not match to test (buffer-size:{buffsize0})."

    _len_checks = len(last_infile0)
    for i in range(_len_checks):
        assert lines_read_backwards01[-_len_checks:][i]==first_infile0[_len_checks-(i+1)], "First lines in {filename0} do not match to test (buffer-size:{buffsize1})."
        assert lines_read_backwards01[i]==last_infile0[_len_checks-(i+1)], "Last lines in {filename0} do not match to test (buffer-size:{buffsize1})."

    _len_checks = len(last_infile0)
    for i in range(_len_checks):
        assert lines_read_backwards02[-_len_checks:][i]==first_infile0[_len_checks-(i+1)], "First lines in {filename0} do not match to test (buffer-size:{buffsize2})."
        assert lines_read_backwards02[i]==last_infile0[_len_checks-(i+1)], "Last lines in {filename0} do not match to test (buffer-size:{buffsize2})."

    _len_checks = len(last_infile0)
    for i in range(_len_checks):
        assert lines_read_backwards03[-_len_checks:][i]==first_infile0[_len_checks-(i+1)], "First lines in {filename0} do not match to test (buffer-size:{buffsize3})."
        assert lines_read_backwards03[i]==last_infile0[_len_checks-(i+1)], "Last lines in {filename0} do not match to test (buffer-size:{buffsize3})."

    # read file backwards now, filename1 (should be the same as filename0)
    lines_read_backwards10 = _run_readline(fn=filename1, bs=buffsize0)
    lines_read_backwards11 = _run_readline(fn=filename1, bs=buffsize1)
    lines_read_backwards12 = _run_readline(fn=filename1, bs=buffsize2)
    lines_read_backwards13 = _run_readline(fn=filename1, bs=buffsize3)
    # outputs for filename0 and filename 1 should be identical
    for f0,f1 in zip(lines_read_backwards00,lines_read_backwards10):
        assert f0==f1, "Lines between {filename0} and  {filename1} do not match to test (buffer-size:{buffsize0})."
    for f0,f1 in zip(lines_read_backwards01,lines_read_backwards11):
        assert f0==f1, "Lines between {filename0} and  {filename1} do not match to test (buffer-size:{buffsize1})."
    for f0,f1 in zip(lines_read_backwards02,lines_read_backwards12):
        assert f0==f1, "Lines between {filename0} and  {filename1} do not match to test (buffer-size:{buffsize3})."
    for f0,f1 in zip(lines_read_backwards03,lines_read_backwards13):
        assert f0==f1, "Lines between {filename0} and  {filename1} do not match to test (buffer-size:{buffsize4})."

    # read file backwards now, filename2 (should be completely empty)
    lines_read_backwards20 = _run_readline(fn=filename2, bs=buffsize0)
    lines_read_backwards21 = _run_readline(fn=filename2, bs=buffsize1)
    lines_read_backwards22 = _run_readline(fn=filename2, bs=buffsize2)
    lines_read_backwards23 = _run_readline(fn=filename2, bs=buffsize3)
    # outputs for filename0 and filename 1 should be identical
    assert lines_read_backwards20==[], "Lines in {filename2} are not empty and do not match to test (buffer-size:{buffsize0})."
    assert lines_read_backwards21==[], "Lines in {filename2} are not empty and do not match to test (buffer-size:{buffsize1})."
    assert lines_read_backwards22==[], "Lines in {filename2} are not empty and do not match to test (buffer-size:{buffsize2})."
    assert lines_read_backwards23==[], "Lines in {filename2} are not empty and do not match to test (buffer-size:{buffsize3})."

def test_readlines():
    """Testing the readlines method in `readBackwards.BackwardsReader`.
    
    Should be the `readline` method output already in a list form."""
    filename0 = "./test_data/test_file0.txt" # bunch of numbers

    # buffer sizes
    buffsize0 = 1000 # in Bytes, 1000 is loads to make sure we get the last 5 lines
    buffsize1 = 4096 # in Bytes, this is loads more than the file, should contain all lines
    buffsize2 = 0 # in Bytes, this should contain all lines
    buffsize3 = -1 # in Bytes, this should contain all lines

    # `readline` should be confirmed so now use it to construct the output of readlines -> check they match
    lines_read_backwards00 = _run_readline(fn=filename0, bs=buffsize0)
    lines_read_backwards00_s = _run_readlines(fn=filename0, bs=buffsize0)
    _one_to_ones_match(lines_read_backwards00,lines_read_backwards00_s,f"file:{filename0}, buffer-size:{buffsize0}")

    lines_read_backwards01 = _run_readline(fn=filename0, bs=buffsize1)
    lines_read_backwards01_s = _run_readlines(fn=filename0, bs=buffsize1)
    _one_to_ones_match(lines_read_backwards01,lines_read_backwards01_s,f"file:{filename0}, buffer-size:{buffsize1}")

    lines_read_backwards02 = _run_readline(fn=filename0, bs=buffsize2)
    lines_read_backwards02_s = _run_readlines(fn=filename0, bs=buffsize2)
    _one_to_ones_match(lines_read_backwards02,lines_read_backwards02_s,f"file:{filename0}, buffer-size:{buffsize2}")

    lines_read_backwards03 = _run_readline(fn=filename0, bs=buffsize3)
    lines_read_backwards03_s = _run_readlines(fn=filename0, bs=buffsize3)
    _one_to_ones_match(lines_read_backwards03,lines_read_backwards03_s,f"file:{filename0}, buffer-size:{buffsize3}")

def test_read_block():
    """Testing the readlines method in `readBackwards.BackwardsReader`.
    
    Should be the `readline` method output already in a list form."""
    filename0 = "./test_data/test_file0.txt" # bunch of numbers

    # buffer sizes
    buffsize0 = 1000 # in Bytes, 1000 is loads to make sure we get the last 5 lines
    buffsize1 = 4096 # in Bytes, this is loads more than the file, should contain all lines
    buffsize2 = 0 # in Bytes, this should contain all lines
    buffsize3 = -1 # in Bytes, this should contain all lines

    # `readline` and `readlines` should now be check to use to test output of `read_block`
    # `read_block` maintains the original order of the file so reverse the backwards line list
    lines_read_backwards00 = _run_readline(fn=filename0, bs=buffsize0)
    lines_read_backwards00.reverse()
    test_block00 = b''.join(lines_read_backwards00)
    lines_read_backwards00_b = _run_read_block(fn=filename0, bs=buffsize0)
    _check_block_match(test_block00,lines_read_backwards00_b,f"file:{filename0}, buffer-size:{buffsize0}")

    lines_read_backwards01 = _run_readline(fn=filename0, bs=buffsize1)
    lines_read_backwards01.reverse()
    test_block01 = b''.join(lines_read_backwards01)
    lines_read_backwards01_b = _run_read_block(fn=filename0, bs=buffsize1)
    _check_block_match(test_block01,lines_read_backwards01_b,f"file:{filename0}, buffer-size:{buffsize1}")

    lines_read_backwards02 = _run_readline(fn=filename0, bs=buffsize2)
    lines_read_backwards02.reverse()
    test_block02 = b''.join(lines_read_backwards02)
    lines_read_backwards02_b = _run_read_block(fn=filename0, bs=buffsize2)
    _check_block_match(test_block02,lines_read_backwards02_b,f"file:{filename0}, buffer-size:{buffsize2}")

    lines_read_backwards03 = _run_readline(fn=filename0, bs=buffsize3)
    lines_read_backwards03.reverse()
    test_block03 = b''.join(lines_read_backwards03)
    lines_read_backwards03_b = _run_read_block(fn=filename0, bs=buffsize3)
    _check_block_match(test_block03,lines_read_backwards03_b,f"file:{filename0}, buffer-size:{buffsize3}")


if(__name__ == "__main__"):
    # try to do a thorough test...

    # test the `readline` method of `readBackwards.BackwardsReader`
    test_readline()
    # test the `readlines` method of `readBackwards.BackwardsReader`
    test_readlines()
    # test the `read_block` method of `readBackwards.BackwardsReader`
    test_read_block()